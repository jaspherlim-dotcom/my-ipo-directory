// Supabase Edge Function：接收 Stripe 付款通知，开通／关闭会员。
// 部署：supabase functions deploy stripe-webhook --no-verify-jwt
// 需要的 secrets：STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET（SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 平台自带）
import Stripe from "npm:stripe@17.7.0";
import { createClient } from "npm:@supabase/supabase-js@2.49.4";

const stripe = new Stripe(Deno.env.get("STRIPE_SECRET_KEY")!);
const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const cryptoProvider = Stripe.createSubtleCryptoProvider();

async function upsertFromSubscription(sub: Stripe.Subscription, userId?: string | null) {
  const customerId = typeof sub.customer === "string" ? sub.customer : sub.customer.id;
  const periodEnd = sub.items?.data?.[0]?.current_period_end ?? (sub as any).current_period_end;
  const row = {
    status: sub.status,
    plan: sub.items?.data?.[0]?.price?.nickname ?? sub.items?.data?.[0]?.price?.id ?? null,
    stripe_customer_id: customerId,
    stripe_subscription_id: sub.id,
    current_period_end: periodEnd ? new Date(periodEnd * 1000).toISOString() : null,
    updated_at: new Date().toISOString(),
  };
  const q = userId
    ? admin.from("members").update(row).eq("user_id", userId)
    : admin.from("members").update(row).eq("stripe_customer_id", customerId);
  const { error } = await q;
  if (error) throw error;
}

Deno.serve(async (req) => {
  const sig = req.headers.get("stripe-signature");
  const body = await req.text();
  let event: Stripe.Event;
  try {
    event = await stripe.webhooks.constructEventAsync(body, sig!, Deno.env.get("STRIPE_WEBHOOK_SECRET")!, undefined, cryptoProvider);
  } catch (e) {
    return new Response(`签名验证失败: ${(e as Error).message}`, { status: 400 });
  }

  try {
    switch (event.type) {
      case "checkout.session.completed": {
        const s = event.data.object as Stripe.Checkout.Session;
        const userId = s.client_reference_id; // 网站在付款链接里带上会员的 user id
        if (!userId) break;
        if (s.mode === "subscription" && s.subscription) {
          const sub = await stripe.subscriptions.retrieve(s.subscription as string);
          await upsertFromSubscription(sub, userId);
        } else {
          // 一次性付款（例如 FPX 买一年）：按网站设定的天数开通
          const days = Number(Deno.env.get("ONE_TIME_ACCESS_DAYS") ?? "365");
          await admin.from("members").update({
            status: "active",
            plan: "one_time",
            stripe_customer_id: (s.customer as string) ?? null,
            current_period_end: new Date(Date.now() + days * 86400000).toISOString(),
            updated_at: new Date().toISOString(),
          }).eq("user_id", userId);
        }
        break;
      }
      case "customer.subscription.updated":
      case "customer.subscription.deleted":
        await upsertFromSubscription(event.data.object as Stripe.Subscription);
        break;
    }
  } catch (e) {
    console.error(e);
    return new Response("处理失败", { status: 500 });
  }
  return new Response(JSON.stringify({ received: true }), { headers: { "content-type": "application/json" } });
});
