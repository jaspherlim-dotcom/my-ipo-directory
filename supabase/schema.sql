-- 马股 IPO 观察站：会员系统（在 Supabase SQL Editor 里执行一次）

-- 1. 会员状态（由 Stripe webhook 写入，用户自己不能改）
create table if not exists public.members (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text,
  status text not null default 'inactive',        -- active / trialing / past_due / canceled / inactive
  plan text,
  stripe_customer_id text unique,
  stripe_subscription_id text,
  current_period_end timestamptz,
  updated_at timestamptz not null default now()
);
alter table public.members enable row level security;
drop policy if exists "members read own row" on public.members;
create policy "members read own row" on public.members
  for select using (auth.uid() = user_id);

-- 2. 付费内容（由 GitHub Actions 用 service key 上传）
create table if not exists public.premium_pages (
  slug text primary key,
  html text not null,
  updated_at timestamptz not null default now()
);
alter table public.premium_pages enable row level security;

-- 网站开关：require_payment = false 时，只要登入就能看；true 时要有效付费会员
create table if not exists public.site_settings (key text primary key, value text not null);
alter table public.site_settings enable row level security;
drop policy if exists "settings public read" on public.site_settings;
create policy "settings public read" on public.site_settings for select using (true);
insert into public.site_settings (key, value) values ('require_payment', 'false')
  on conflict (key) do nothing;
-- 以后要开始收费：update public.site_settings set value = 'true' where key = 'require_payment';

-- 判断目前登入的人能不能看会员内容
create or replace function public.is_active_member() returns boolean
language sql stable security definer set search_path = public as $$
  select auth.uid() is not null and (
    coalesce((select value from public.site_settings where key = 'require_payment'), 'true') = 'false'
    or exists (
      select 1 from public.members m
      where m.user_id = auth.uid()
        and m.status in ('active', 'trialing')
        and (m.current_period_end is null or m.current_period_end > now())
    )
  );
$$;

drop policy if exists "active members read premium" on public.premium_pages;
create policy "active members read premium" on public.premium_pages
  for select using (public.is_active_member());

-- 新用户注册时自动建一行会员资料（状态 inactive）
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.members (user_id, email) values (new.id, new.email)
  on conflict (user_id) do nothing;
  return new;
end;
$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============ 后台：上传招股书（只有管理员能用） ============
-- 3. 管理员名单。把自己加进去（电邮换成你的登入电邮，先在网站登入过一次）：
--    insert into public.admins (user_id) select id from auth.users where email = '你的电邮';
create table if not exists public.admins (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);
alter table public.admins enable row level security;  -- 不开放任何读写，只能在 SQL Editor 改

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select auth.uid() is not null and exists (select 1 from public.admins a where a.user_id = auth.uid());
$$;

-- 4. 上传纪录：后台每上传一份就加一行，GitHub Actions 处理完把 status 改成 done / failed
create table if not exists public.prospectus_uploads (
  id bigint generated always as identity primary key,
  path text not null,                 -- Storage 里的位置
  file_name text,
  bursa_url text,
  slug text,                          -- 留空 = 让程序按公司名自动判断
  status text not null default 'pending',   -- pending / done / failed
  message text,
  uploaded_by uuid default auth.uid(),
  created_at timestamptz not null default now(),
  processed_at timestamptz
);
alter table public.prospectus_uploads enable row level security;
drop policy if exists "admins read uploads" on public.prospectus_uploads;
create policy "admins read uploads" on public.prospectus_uploads for select using (public.is_admin());
drop policy if exists "admins add uploads" on public.prospectus_uploads;
create policy "admins add uploads" on public.prospectus_uploads for insert
  with check (public.is_admin() and status = 'pending');

-- 5. 私人文件夹（不公开），只收 PDF，单个最大 50MB
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('prospectus', 'prospectus', false, 52428800, array['application/pdf'])
on conflict (id) do nothing;
drop policy if exists "admins upload prospectus" on storage.objects;
create policy "admins upload prospectus" on storage.objects for insert
  with check (bucket_id = 'prospectus' and public.is_admin());
drop policy if exists "admins read prospectus" on storage.objects;
create policy "admins read prospectus" on storage.objects for select
  using (bucket_id = 'prospectus' and public.is_admin());
