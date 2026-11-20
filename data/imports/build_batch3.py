"""一次性脚本：2026-11-20 整理 Big Caring、YES Group、EcoSys。"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build_batch2 import F, U, A  # noqa
T = "https://www.thestar.com.my/business/business-news/"
out = []

a, b, c = T+"2026/10/29/big-caring-plans-to-raise-rm6378mil-from-main-market-ipo", T+"2026/11/10/public-portion-of-big-caring-ipo-431-times-oversubscribed", "https://thesun.my/business/big-caring-group-plans-40-to-50-new-outlets-annually-over-next-three-to-five-years/"
def P(pct, item): return {"item": item, "rm": round(637800000*pct/100), "src": [a, c], "note": f"原文只给 {pct}%，金额由本站按 RM637.8 百万计算"}
out.append({"slug":"big-caring","name":"Big Caring Group Bhd","name_zh":"Big Caring（大众关怀药房）","sector_zh":"零售 · 连锁药房","one_liner":"全国 600 多间门店的连锁药房，靠卖药品、保健品和个人护理产品赚钱。",
 "facts":{"market":{"v":"Main","src":[a,c]},"business":{"v":"马来西亚零售药房连锁，2006 年由一间店起家，现已超过 600 间门店，遍布全国 13 州；经营医疗保健、药品及保健品；计划未来 3 至 5 年每年开 40 至 50 间新店，并考虑收购及建新配送中心。现有 Bukit Raja 配送中心使用率 80.2%（截至 2026 年 9 月 30 日）。","src":[a,c]},
  "issue_price_rm":{"v":1.08,"src":[a,c],"note":"The Star 写为“最高 IPO 价”"},"new_shares":{"v":590500000,"src":[a,c],"note":"占扩大后股本 8%"},"ofs_shares":{"v":1300000000,"src":[a,c],"note":"占扩大后股本 17.5%"},
  "proceeds_rm":{"v":637800000,"src":[a,c],"note":"公开发售新股所得（毛额）"},"market_cap_rm":{"v":8000000000,"src":[a,c],"note":"约 RM80 亿"},"enlarged_shares":{"v":7400000000,"src":[a]},
  "prospectus_date":{"v":"2026-10-29","src":[c]},"listing_date":{"v":"2026-11-19","src":[a]},
  "oversub_public":{"v":4.31,"src":[b],"note":"土著部分约 0.94 倍（认购不足），其他马来西亚公众部分约 7.68 倍"},"applications":{"v":29474,"src":[b]},
  "adviser":{"v":"Maybank IB、RHB IB、AmInvestment Bank（联合主要顾问）；UBS（联合全球协调人）","src":[a]}},
 "use_of_proceeds":[P(89.5,"偿还银行借款"),P(4.7,"设立新配送中心（36 个月内）"),P(5.8,"上市费用")],
 "quotes":[{"who":"Livia Chan，董事","text":"Same-store sales growth remained healthy at high single digits","src":c}],
 "source_meta":{a:{"title":"Big Caring plans to raise RM637.8mil from Main Market IPO","publisher":"The Star","date":"2026-10-29"},b:{"title":"Public portion of Big Caring IPO 4.31 times oversubscribed","publisher":"The Star","date":"2026-11-10"},c:{"title":"Big Caring Group plans 40 to 50 new outlets annually over next three to five years","publisher":"The Sun","date":"2026-10-29"}},
 "todo_official":"待补：最终发行价、首日表现、招股书财务数据。中文名为本站暂译。",
 "analysis":A("Big Caring 是今年最大的零售 IPO 之一：600 多间药房，市值约 RM80 亿。但要看清楚，公司拿到的钱近九成是拿去还银行，不是开新店。",
  [("全国各地的一般消费者、病患与保健品买家。","inference"),("社区里随处可见、价格有竞争力、有药剂师咨询的一站式健康商店。","inference"),("600 多间实体门店，覆盖 13 州。","fact"),("会员制度与药剂师服务（新闻未详述）；同店销售增长维持高单位数。","fact"),("药品、保健品、个人护理产品零售。","fact"),("门店网络、Bukit Raja 配送中心（使用率 80.2%）。","fact"),("采购、物流配送、开店与门店营运。","fact"),("药厂与品牌供应商、物业业主。","inference"),("货品成本、店租、人事、物流；还债后利息成本会下降。","inference")],
  "护城河在于门店密度与采购规模：店越多，向药厂拿货越便宜，物流越有效率。",
  "约 89.5% 的新股所得用来还银行借款，所以这次 IPO 更像“降负债 + 让老股东套现部分股份”，增长资金主要靠内部现金流。",
  ["每年新开 40-50 间店的进度","同店销售增长","还债后的利息节省与净利率","与 Watsons、Guardian、其他连锁药房的竞争"],
  "大型、业务易懂的消费股，但土著部分认购不足、公众部分只超额认购 4.31 倍，反映市场对 RM80 亿估值有保留。",
  ["连锁的威力在于规模经济：采购、物流、品牌一起放大。","同店销售增长比开新店更能说明生意是否健康。"],
  [("估值","以 RM1.08 计市值约 RM80 亿，需对照盈利判断是否偏贵。","inference"),("竞争","连锁药房与个人护理零售竞争激烈。","inference"),("募资主要用于还债","增长主要靠内部现金流，不是新资金。","fact")],based="s1")})

a, b = T+"2026/11/05/yes-group-aims-to-raise-rm1654mil-from-its-ipo", T+"2026/11/17/yes-group-ipo-public-portion-subscribed-280-times-ahead-of-ace-market-debut"
out.append({"slug":"yes-group","name":"Yes Group Management Bhd","name_zh":"Yes Group（Yes Travel）","sector_zh":"服务 · 商务奖励旅游（MICE）","one_liner":"帮企业安排奖励旅游、会议和展览行程的 MICE 旅游公司。",
 "facts":{"market":{"v":"ACE","src":[a,b]},"business":{"v":"经营 Yes Travel 品牌，为企业客户提供 MICE（会议、奖励旅游、大会及展览）旅游与活动管理服务；计划扩展欧洲地面交通服务、在英国设区域办事处服务英国和德国等西欧客户，并设立 Yes Academy（目标每年 100 名学员）。","src":[a,b]},
  "issue_price_rm":{"v":0.18,"src":[a,b]},"new_shares":{"v":91870000,"src":[a,b]},"ofs_shares":{"v":45930000,"src":[b]},"proceeds_rm":{"v":16540000,"src":[a,b],"note":"公开发售新股所得"},
  "app_close":{"v":"2026-11-13","src":[a]},"listing_date":{"v":"2026-11-26","src":[a,b]},
  "oversub_public":{"v":2.8,"src":[b],"note":"⚠ 原文写 “subscribed 2.80 times”（认购倍数），口径可能与超额认购不同；土著部分 0.49 倍、其他公众部分 5.11 倍"},"applications":{"v":2053,"src":[b]},
  "adviser":{"v":"Malacca Securities Sdn Bhd（主要顾问、保荐人、包销商及配售代理）","src":[b]}},
 "use_of_proceeds":U([("扩展欧洲地面交通服务、设英国办事处",6500000),("设立 Yes Academy",3000000),("一般营运资金",3040000),("上市费用",4000000)],a),
 "quotes":[{"who":"Mak Shau Kwan，董事经理","text":"Having our own operations in the United Kingdom will improve cost efficiency","src":a}],
 "source_meta":{a:{"title":"YES Group aims to raise RM16.54mil from its IPO","publisher":"The Star","date":"2026-11-05"},b:{"title":"Yes Group IPO public portion subscribed 2.80 times ahead of ACE Market debut","publisher":"The Star","date":"2026-11-17"}},
 "analysis":A("公司奖励业绩好的员工去欧洲玩，背后要有人订机票、安排车、包场地，Yes Group 就是做这个的。它现在想在英国自己设点，把外包给当地的钱赚回来。",
  [("企业客户（奖励旅游、会议、展览的主办方）。","fact"),("一站式安排团体行程与活动，客户只要讲预算和目的地。","inference"),("直接对企业销售。","inference"),("回头客为主，企业每年都有奖励旅游与年会。","inference"),("MICE 项目收费（行程、交通、活动管理）。","fact"),("供应商网络、团队执行经验、即将设立的英国办事处。","fact"),("行程设计、供应商采购、现场执行。","inference"),("航空公司、酒店、欧洲地面交通业者。","inference"),("机票、酒店、交通等外购成本占大头，利润率取决于议价能力。","inference")],
  "护城河在于企业客户关系与执行口碑；在欧洲自营地面交通，有机会把外包利润留在自己手上。",
  "RM6.5 百万押注欧洲（英国办事处 + 地面交通），上市费用 RM4 百万约占募资 24%。",
  ["欧洲业务的利润贡献","企业客户的回头率","旅游需求与经济周期","汇率（英镑、欧元）"],
  "很小的 IPO（18 仙），公众认购偏冷、土著部分认购不足。旅游业受经济周期影响大，企业一削预算，奖励旅游往往第一个被砍。",
  ["把外包环节自己做（像在英国自设交通），是提高毛利的方法，但也增加固定成本。","服务业上市可以“卖培训”：Yes Academy 把经验变成另一条收入线。"],
  [("经济周期","企业削减开支时，奖励旅游预算首当其冲。","inference"),("海外扩张执行","在英国设点涉及人事、法规与成本控制。","inference"),("认购偏冷","土著部分只认购 0.49 倍。","fact"),("财务资料尚未收录","本站未有收入与利润资料。","unknown")])})

a, b, c = T+"2026/09/23/ecosys-seeks-to-raise-rm3934mil-from-ace-market-ipo", T+"2026/10/01/ecosys-malaysia-ipo-public-portion-oversubscribed-2067-times", T+"2026/10/14/ecosys-shares-soar-179-in-morning-trade"
out.append({"slug":"ecosys","name":"EcoSys (Malaysia) Bhd","name_zh":"EcoSys","sector_zh":"科技 · 半导体设备与废气处理","one_liner":"为半导体业制造超高纯度精密部件和废气处理系统，印度是重要市场。",
 "facts":{"market":{"v":"ACE","src":[a,b]},"business":{"v":"工业解决方案供应商，为半导体及相关行业制造超高纯度（UHP）精密工程部件与子组件，以及废气处理系统（abatement systems）；印度市场在 FY2025 占集团收入 35.1%，印度废气处理业务新增 7 名客户，并计划在印度设销售与服务中心。","src":[a]},
  "issue_price_rm":{"v":0.27,"src":[a,c]},"new_shares":{"v":145700000,"src":[a]},"proceeds_rm":{"v":39340000,"src":[a],"note":"全部为新股，没有献售旧股"},
  "listing_date":{"v":"2026-10-14","src":[b,c]},"oversub_public":{"v":206.7,"src":[b],"note":"土著部分 136.77 倍，其他公众部分 276.63 倍"},"applications":{"v":31734,"src":[b]},
  "adviser":{"v":"M&A Securities Sdn Bhd（主要顾问、保荐人、包销商及配售代理）；Eco Asia Capital Advisory（财务顾问）","src":[a]}},
 "use_of_proceeds":U([("扩展废气处理业务（采购关键组件与模块）",17000000),("偿还银行借款",8000000),("购买机器、增聘员工",4930000),("扩展印度业务",1540000),("营运资金",2360000),("上市费用",5500000)],a),
 "financials":[{"label":"印度市场收入","period":"FY2025","rm":38220000,"src":[a],"note":"只是印度部分，占集团收入 35.1%；新闻未给集团总收入"}],
 "quotes":[{"who":"Chan Chee Wei，董事经理","text":"We believe these initiatives will enhance our ability to serve customers","src":a}],
 "source_meta":{a:{"title":"EcoSys seeks to raise RM39.34mil from ACE Market IPO","publisher":"The Star","date":"2026-09-23"},b:{"title":"EcoSys Malaysia IPO public portion oversubscribed 206.7 times","publisher":"The Star","date":"2026-10-01"},c:{"title":"Ecosys shares soar 179% in ACE Market debut","publisher":"The Star","date":"2026-10-14"}},
 "analysis":A("芯片厂会排出有毒废气，一定要处理才能排放。EcoSys 一边做这类废气处理系统，一边做超高纯度零件，等于站在半导体扩厂潮的“必需品”位置，而且三分之一收入来自正在大建芯片厂的印度。",
  [("半导体及相关行业的工厂，包括印度客户。","fact"),("超高纯度部件与废气处理，帮芯片厂符合环保与制程要求。","inference"),("直接销售，计划在印度设销售与服务中心。","fact"),("设备装好后需要维护服务，形成长期关系。","inference"),("部件制造 + 废气处理系统销售；印度 FY2025 收入 RM38.22 百万。","fact"),("超高纯度制造能力、废气处理技术、印度客户群。","fact"),("精密制造、系统组装、安装与服务。","inference"),("半导体设备商与芯片厂。","inference"),("关键组件采购、机器、人员；募资 RM17 百万用于采购组件扩展废气处理业务。","fact")],
  "超高纯度与废气处理有技术门槛和客户认证，比一般机械加工更难被取代。",
  "最大一笔 RM17 百万投入废气处理业务，RM8 百万还债，RM1.54 百万开拓印度。",
  ["印度客户与订单增长","半导体资本开支周期","首日暴涨后的估值是否透支","毛利率"],
  "公众超额认购 206.7 倍，首日早盘一度大涨（据 The Star 标题为 179%），短期情绪非常热。追高前要冷静对照盈利与估值。",
  ["在热门产业里找“必需又没人想做”的环节，比如废气处理。","海外市场占比高时，要在当地设服务点，才能守住客户。"],
  [("估值透支","首日大涨后股价可能已反映多年增长。","inference"),("半导体周期","芯片业资本开支放缓会直接影响订单。","inference"),("印度市场集中","印度占收入 35.1%，当地政策或项目延误影响大。","fact")])})

pathlib.Path(__file__).with_name("batch3.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out))
