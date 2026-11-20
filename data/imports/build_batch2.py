"""一次性脚本：把 2026-11-20 人工整理的 7 家 IPO 资料写成 import 格式。来源均为 The Star。"""
import json, pathlib
T = "https://www.thestar.com.my/business/business-news/"
def F(v, u, note=None):
    d = {"v": v, "src": [u]}
    if note: d["note"] = note
    return d
def U(items, u): return [{"item": i, "rm": r, "src": [u]} for i, r in items]
def A(summary, bmc, moat, money, watch, inv, sme, risks, based="s1"):
    keys = ["customer_segments","value_propositions","channels","customer_relationships","revenue_streams","key_resources","key_activities","key_partners","cost_structure"]
    return {"generated_by":"ai","model":"claude-opus-5-5","generated_at":"2026-11-20","reviewed":False,"based_on":[based],
            "summary":summary,"bmc":{k:{"text":t,"basis":b} for k,(t,b) in zip(keys,bmc)},"moat":moat,"money_flow":money,
            "watch":watch,"investor_takeaway":inv,"sme_lessons":sme,"risks":[{"title":a,"detail":b,"basis":c} for a,b,c in risks]}
out = []

u = T+"2026/10/23/keb-to-raise-rm4849mil-from-ace-market-ipo"
out.append({"slug":"keb","name":"KEB Bhd","name_zh":"KEB","sector_zh":"房地产 · 物业发展","one_liner":"建屋兼自己当承包商的物业发展商：自建自卖，赚的是发展利润。",
 "facts":{"market":F("ACE",u),"business":F("物业发展商，自 2004 年起完成 14 个发展项目，涵盖住宅、工业、商业及综合用途，由内部建筑子公司 KEB Utama（CIDB G7 承包商）负责施工。目前 4 个在建项目总发展价值（GDV）约 RM13.6 亿，另有 2 个未来项目约 RM3.83 亿；土地储备约 60.01 英亩（含合营土地）。",u),
  "issue_price_rm":F(0.35,u),"new_shares":F(138540000,u),"proceeds_rm":F(48490000,u,"公开发售新股所得"),"prospectus_date":F("2026-10-23",u),"app_open":F("2026-10-23",u),"app_close":F("2026-11-02",u),"listing_date":F("2026-11-16",u,"文章发布时为预定上市日"),
  "adviser":F("M&A Securities Sdn Bhd（主要顾问、保荐人、包销商及配售代理）；Eco Asia Capital Advisory（财务顾问）",u)},
 "use_of_proceeds":U([("收购发展用地",19000000),("项目发展营运资金",14890000),("偿还银行借款",8500000),("上市费用",6100000)],u),
 "financials":[{"label":"收入","period":"2026 年上半年","rm":136800000,"src":[u],"note":"同期毛利 RM45 百万，毛利率 32.89%"},{"label":"净利","period":"2026 年上半年","rm":22790000,"src":[u]},{"label":"收入","period":"2026 年第二季","rm":54000000,"src":[u]},{"label":"净利","period":"2026 年第二季","rm":6780000,"src":[u]}],
 "quotes":[{"who":"Datuk Lim Kim Chong，董事经理","text":"The IPO will strengthen our financial position and provide us with additional resources to expand our landbank","src":u}],
 "source_meta":{u:{"title":"KEB to raise RM48.49mil from ACE Market IPO","publisher":"The Star","date":"2026-10-23"}},
 "analysis":A("KEB 是“自己买地、自己建、自己卖”的发展商，自家有 G7 承包商，所以建筑利润也留在家里。募资最大一笔拿去买地，说明它要的是下一批项目。",
  [("买房的住户、需要厂房或店面的业者。","inference"),("一条龙开发：从土地、建筑到销售，中间少一层承包商利润，成本较可控。","inference"),("项目现场销售、代理与网络营销；新闻未说明。","unknown"),("一次性买卖，口碑影响下一个项目的销售。","inference"),("卖房、厂房和商业单位的发展收入；2026 上半年收入 RM136.8 百万。","fact"),("约 60 英亩土地储备、G7 建筑子公司、22 年开发经验。","fact"),("购地、规划审批、施工、销售。","fact"),("合营土地的地主、银行（贷款）、分包商。","fact"),("土地成本、建材与人工、融资利息；上半年毛利率 32.89%。","fact")],
  "护城河在于自有施工能力和土地储备，但物业发展高度依赖地点与周期，护城河有限。",
  "约 39% 募资（RM19 百万）用于买地，另有 RM8.5 百万还银行贷款，属于“补地 + 降负债”。",
  ["未入账销售（unbilled sales）与新推案的销售率","土地储备能撑几年","负债比率","利率与房市周期"],
  "上半年净利 RM22.79 百万，但物业发展盈利常随项目进度起伏，单看半年数字容易高估。要看未来几年的推案管道。",
  ["自己做承包商可以把利润留在家里，但也要能承担工程风险。","土地是发展商的“原料库存”，补地节奏决定未来几年饭碗。"],
  [("房市周期","房市放缓会直接影响新推案的销售。","inference"),("项目集中","在建项目数量不多，单一项目延误影响大。","inference"),("盈利起伏","发展商盈利依项目完工进度确认，季度波动大。","inference")])})

u = T+"2026/08/18/butterfield-fb-to-raise-rm72mil-from-ace-market-ipo-for-business-expansion"
out.append({"slug":"butterfield-fb","name":"Butterfield FB Bhd","name_zh":"Butterfield FB","sector_zh":"消费 · 咖啡茶预混粉制造","one_liner":"槟城的咖啡、茶提取物预混粉制造商，帮品牌做“三合一”背后的粉。",
 "facts":{"market":F("ACE",u),"business":F("咖啡及茶提取物粉末预混产品制造商，总部位于槟城 Bukit Minyak；IPO 后扩建总部，增加约 29,170 平方英尺生产空间及 9,954 平方英尺仓储，并装设年产能 4,095 公吨的第四条生产线。",u),
  "issue_price_rm":F(0.48,u),"new_shares":F(150000000,u),"ofs_shares":F(72000000,u),"proceeds_rm":F(72000000,u,"公开发售新股所得"),"market_cap_rm":F(384000000,u,"以 IPO 价及扩大后股本 8 亿股计算"),"enlarged_shares":F(800000000,u),
  "prospectus_date":F("2026-08-18",u),"app_open":F("2026-08-18",u),"app_close":F("2026-09-02",u),"listing_date":F("2026-09-15",u,"文章发布时为预定上市日"),"adviser":F("M&A Securities Sdn Bhd（顾问、保荐人、包销商及配售代理）",u)},
 "use_of_proceeds":U([("扩建槟城 Bukit Minyak 总部",15200000),("营运资金",37800000),("策略投资、合并或收购（目标为即溶咖啡与茶预混品牌）",13000000),("上市费用",6000000)],u),
 "source_meta":{u:{"title":"Butterfield FB to raise RM72mil from ACE Market IPO for business expansion","publisher":"The Star","date":"2026-08-18"}},
 "analysis":A("你喝的三合一咖啡，背后可能不是品牌自己磨的粉。Butterfield 就是做这种预混粉的工厂，现在还想拿钱去收购品牌，从“幕后”走到“台前”。",
  [("新闻未说明客户类型；募资计划收购即溶咖啡与茶预混品牌，显示它和这些品牌在同一条产业链。","inference"),("规模化生产预混粉，帮品牌省下自建工厂的成本。","inference"),("B2B 直接供货；新闻未说明。","unknown"),("代工关系通常较长期，配方和品质认证造成转换成本。","inference"),("销售预混粉产品；收入数字新闻未披露。","fact"),("槟城工厂、三条现有生产线 + 第四条新线（4,095 公吨）。","fact"),("配方研发、生产、仓储。","fact"),("咖啡、茶叶、奶粉、糖等原料供应商；未具名。","inference"),("原料成本（咖啡豆、奶粉、糖）占大头，价格波动大。","inference")],
  "护城河来自产能规模与配方能力；若成功收购品牌，就多了一层品牌溢价。",
  "最大一笔 RM37.8 百万用作营运资金，另 RM13 百万留给收购品牌，说明管理层想往上游品牌延伸。",
  ["第四条生产线的使用率","原料价格对毛利率的影响","收购哪个品牌、付多少钱","出口比例"],
  "以 IPO 价算市值 RM3.84 亿，新闻没有披露盈利，估值是否合理要看招股书的财务数字。",
  ["代工厂往品牌走是常见升级路线，但品牌要的是营销能力，不只是工厂。","产能先行要配合订单，否则新厂房就是成本。"],
  [("原料价格","咖啡、奶粉、糖价格波动会直接压缩利润。","inference"),("收购风险","以 RM13 百万收购品牌，价格与整合能力决定成败。","inference"),("财务资料尚未收录","本站未有收入与利润资料，请先读招股书。","unknown")])})

u = T+"2026/04/15/manforce-eyes-rm304mil-from-ace-market-ipo-listing-set-for-may-6"
out.append({"slug":"manforce","name":"Manforce Group Bhd","name_zh":"Manforce","sector_zh":"服务 · 外劳管理与宿舍","one_liner":"帮工厂请外劳、管外劳、安排宿舍的人力服务公司。",
 "facts":{"market":F("ACE",u),"business":F("外籍劳工管理服务、人力供应服务及宿舍管理方案的综合供应商。",u),"issue_price_rm":F(0.38,u),"new_shares":F(79990000,u),"ofs_shares":F(19990000,u),"proceeds_rm":F(30400000,u,"新闻所写的募资总额"),"enlarged_shares":F(399980000,u),
  "prospectus_date":F("2026-04-15",u),"app_open":F("2026-04-15",u),"app_close":F("2026-04-21",u),"ballot_date":F("2026-04-24",u),"listing_date":F("2026-05-06",u,"文章发布时为预定上市日"),"adviser":F("M & A Securities Sdn Bhd（主要顾问、保荐人、包销商及配售代理）；Eco Asia Capital Advisory（财务顾问）",u)},
 "use_of_proceeds":U([("扩展业务营运（新增招聘配额）",14740000),("提升资讯科技与营运系统",4640000),("营运资金",6320000),("上市费用",4700000)],u),
 "quotes":[{"who":"Datuk Wong Boon Ming，董事经理","text":"We are humbled by the strong response and confidence shown by investors.","src":u}],
 "source_meta":{u:{"title":"Manforce eyes RM30.4mil from ACE market IPO, listing set for May 6","publisher":"The Star","date":"2026-04-15"}},
 "analysis":A("马来西亚工厂长期缺人，Manforce 做的就是“包办外劳”：帮你请、帮你管、帮你安排住。赚的是服务费，最大的变数是政府政策。",
  [("需要外劳的制造业、种植业、建筑业雇主（新闻只说外劳服务，行业为推论）。","inference"),("雇主不用自己处理配额、准证、宿舍等繁琐事务。","inference"),("直接对雇主销售。","inference"),("长期服务合约，外劳在岗期间持续收费。","inference"),("外劳管理费、人力供应费、宿舍管理费。","fact"),("政府批准的招聘配额、宿舍设施、合规经验。","inference"),("招聘、准证办理、宿舍管理、外劳调配。","fact"),("来源国中介、政府部门、宿舍业主。","inference"),("人事、宿舍租金与维护、合规成本。","inference")],
  "护城河主要是配额与合规记录，政府政策一改，护城河可能一夜变小。",
  "近一半募资（RM14.74 百万）用来扩充招聘配额，说明增长关键是“能拿多少配额”。",
  ["外劳政策与配额变化","宿舍使用率","客户集中度","人权与劳工合规事件"],
  "需求是真的，但这是高度受政策左右的行业。投资前要读招股书里的客户集中度和监管风险章节。",
  ["别人嫌麻烦的事，可以变成生意。","受政策影响大的行业，合规就是最大资产。"],
  [("政策风险","外劳配额、冻结招聘或收费政策改变会直接影响业务。","inference"),("劳工合规与声誉","外劳福利问题可能引起国际买家与监管关注。","inference"),("财务资料尚未收录","本站未有收入与利润资料。","unknown")])})

u = T+"2026/05/25/ace-market-bound-eckem-holdings-aims-to-rise-rm15mil-from-ipo"
out.append({"slug":"eckem","name":"Eckem Holdings Bhd","name_zh":"Eckem","sector_zh":"工业 · 化学品分销","one_liner":"代理欧洲品牌工业化学品的分销商，也有橡胶产品业务。",
 "facts":{"market":F("ACE",u),"business":F("工业化学品分销商，代理的品牌多数来自欧洲，并正洽谈更多品牌在马来西亚与新加坡的代理权；另有橡胶产品分部，计划增设生产线。",u),"issue_price_rm":F(0.12,u),"new_shares":F(125000000,u),"proceeds_rm":F(15000000,u,"公开发售新股所得"),
  "prospectus_date":F("2026-05-25",u),"app_open":F("2026-05-25",u),"app_close":F("2026-06-19",u),"listing_date":F("2026-07-03",u,"文章发布时为预定上市日"),"adviser":F("M&A Securities（顾问、保荐人、包销商及配售代理）",u)},
 "use_of_proceeds":U([("兴建新办公室、仓库及实验室",6000000),("橡胶产品分部新生产线",2000000),("偿还银行借款",1450000),("营运资金",1750000),("上市费用",3800000)],u),
 "quotes":[{"who":"Jack Tan，执行董事","text":"Those discussions are still ongoing, and we should be able to see some positive results as early as this year","src":u}],
 "source_meta":{u:{"title":"ACE Market-bound Eckem Holdings aims to raise RM15mil from IPO","publisher":"The Star","date":"2026-05-25"}},
 "analysis":A("Eckem 是典型的“代理商”：把欧洲品牌的工业化学品卖给本地工厂。代理权就是饭碗，所以它一直在谈新品牌。",
  [("需要工业化学品的本地与新加坡工厂（具体行业未披露）。","inference"),("让本地工厂买得到欧洲品牌化学品，并提供技术支援与库存。","inference"),("直接销售团队；实验室可能用于为客户测试配方。","inference"),("长期供货关系，技术服务增加粘性。","inference"),("化学品分销差价 + 橡胶产品销售。","fact"),("欧洲品牌代理权、仓库、新实验室。","fact"),("采购、仓储、技术销售、少量橡胶产品制造。","fact"),("欧洲化学品品牌原厂。","fact"),("采购成本、仓储物流、汇率（欧元）。","inference")],
  "护城河在于代理权，但代理权可以被原厂收回或转给别人，这是分销商最大的隐忧。",
  "RM6 百万盖办公室、仓库和实验室，上市费用 RM3.8 百万约占募资 25%，比例偏高。",
  ["新代理权谈判结果","橡胶产品新线的贡献","欧元汇率","前几大品牌占收入比例"],
  "小型分销股（IPO 价 12 仙），看点在新代理权能否带来增长；新闻没有盈利数字，估值无法判断。",
  ["代理生意要不断加新品牌，降低单一原厂依赖。","加一个实验室，就把“卖货”升级成“卖技术服务”。"],
  [("代理权风险","原厂终止代理会直接影响收入。","inference"),("汇率","以欧洲品牌为主，欧元走强会提高成本。","inference"),("财务资料尚未收录","本站未有收入与利润资料。","unknown")])})

u = T+"2026/03/27/ace-market-bound-ams-advanced-material-aims-to-raise-rm3277mil-from-ipo"
out.append({"slug":"ams-advanced-material","name":"AMS Advanced Material Bhd","name_zh":"AMS Advanced Material","sector_zh":"工业 · 铝铜材料","one_liner":"铝和铜材料供应商，加工后卖给半导体与工程支援业者，也做铝制建材。",
 "facts":{"market":F("ACE",u),"business":F("铝和铜产品供应商，扩展增值铝材加工能力以服务半导体与工程支援行业，目标成为一站式供应商；计划在槟城设持牌制造仓库、扩展铝制建筑产品制造，并在彭亨关丹设分销点。",u),"issue_price_rm":F(0.29,u),"proceeds_rm":F(32770000,u,"新闻所写的 IPO 募资额"),"market_cap_rm":F(177480000,u),"enlarged_shares":F(612000000,u),
  "prospectus_date":F("2026-03-27",u),"app_open":F("2026-03-27",u),"app_close":F("2026-04-10",u),"listing_date":F("2026-04-23",u,"文章发布时为预定上市日"),"adviser":F("M & A Securities Sdn Bhd（主要顾问、保荐人、包销商及配售代理）",u)},
 "use_of_proceeds":U([("槟城持牌制造仓库",8100000),("扩展铝制建筑产品制造",6890000),("关丹新分销点",2500000),("偿还借款",8160000),("营运资金",2670000),("上市费用",4430000)],u),
 "quotes":[{"who":"Keith Keh Teng Yang，董事经理","text":"We are operating at almost full capacity. The new facilities will allow us to complement and increase our capacities,","src":u}],
 "source_meta":{u:{"title":"ACE Market-bound AMS Advanced Material aims to raise RM32.77mil from IPO","publisher":"The Star","date":"2026-03-27"}},
 "analysis":A("AMS 卖的是铝和铜，但想赚的不只是“卖材料”的钱，而是加工后的增值钱，特别是给槟城半导体业者用的精密材料。",
  [("半导体与工程支援业者，以及建筑业（铝制建材）。","fact"),("一站式：材料 + 加工，客户少找一个供应商。","fact"),("分销点（如新设的关丹据点）与直接销售。","fact"),("供应链关系，半导体客户认证后较稳定。","inference"),("材料销售 + 增值加工 + 铝制建材。","inference"),("仓库与加工设备；管理层称产能几乎全满。","fact"),("采购、切割与加工、仓储、分销。","inference"),("铝铜原料供应商、半导体客户。","inference"),("金属原料成本（随 LME 价格波动）、设备折旧。","inference")],
  "单纯卖材料护城河很浅；增值加工和半导体客户认证才是差异化来源。",
  "RM8.16 百万（约 25%）用来还债，其余投向新仓库、建材产能和关丹分销点。",
  ["新仓库与产线投产后的产能利用率","铝、铜价格对毛利的影响","半导体客户订单","还债后的利息节省"],
  "管理层说产能几乎全满，扩产有道理；但金属价格波动会让盈利起伏，要看招股书的毛利率历史。",
  ["从卖原料走向卖加工服务，是贸易商提升毛利的典型路线。","产能全满时扩张，比先建厂再找客户安全。"],
  [("金属价格波动","铝铜价格起落会影响库存价值和毛利。","inference"),("半导体周期","半导体行业放缓会减少加工需求。","inference"),("财务资料尚未收录","本站未有收入与利润资料。","unknown")])})

u = T+"2026/01/21/ace-market-bound-kee-ming-group-to-raise-rm3150mil-from-ipo"
out.append({"slug":"kee-ming","name":"Kee Ming Group Bhd","name_zh":"Kee Ming","sector_zh":"工程 · 机电（再生能源 / 数据中心）","one_liner":"做机电工程的承包商，主攻再生能源并网、数据中心和工厂项目。",
 "facts":{"market":F("ACE",u),"business":F("综合机电（M&E）工程方案供应商，三大核心业务：再生能源并网（interconnection）工程、数据中心，以及工业设计与建造项目（工厂、半导体设施、物流中心）；曾为超大规模云服务商承接数据中心项目。",u),"issue_price_rm":F(0.38,u),"new_shares":F(66630000,u),"ofs_shares":F(16250000,u),
  "proceeds_rm":F(25300000,u,"公开发行新股所得；连同献售旧股，IPO 总额为 RM31.50 百万"),"market_cap_rm":F(123500000,u),"enlarged_shares":F(325000000,u),
  "prospectus_date":F("2026-01-21",u),"app_open":F("2026-01-21",u),"app_close":F("2026-01-27",u),"listing_date":F("2026-02-12",u,"文章发布时为预定上市日"),"adviser":F("TA Securities（主要顾问、保荐人、独家包销商及配售代理）；Eco Asia Capital Advisory（财务顾问）",u)},
 "use_of_proceeds":U([("未来项目营运资金",13000000),("未来项目履约保证金",4000000),("公司扩张",1720000),("购买 ERP 系统",1000000),("一般营运资金",598000),("上市费用",5000000)],u),
 "quotes":[{"who":"Liew Kar Hoe，董事经理","text":"We see interconnection facilities work as a sustainable business and will last for many years,","src":u}],
 "source_meta":{u:{"title":"ACE Market-bound Kee Ming Group to raise RM31.50mil from IPO","publisher":"The Star","date":"2026-01-21"}},
 "analysis":A("Kee Ming 跟 MyDCD 有点像，都是数据中心热潮的“卖铲人”，但它多了一条再生能源并网的腿：太阳能电站要接上电网，就需要它这类承包商。",
  [("再生能源电站业主、数据中心（含超大规模云服务商）、工厂与物流中心业主。","fact"),("一家公司搞定并网、数据中心与厂房机电，有相关项目记录。","inference"),("项目投标与过往客户推荐。","inference"),("项目制，靠执行记录拿下一单。","inference"),("机电工程合约收入；比例未披露。","inference"),("工程团队、并网与数据中心项目经验。","fact"),("设计、施工、测试与并网。","fact"),("设备供应商、分包商、银行（保证金）。","inference"),("材料、分包、人工；需垫付营运资金与履约保证金。","fact")],
  "并网工程需要特定资质与经验，门槛比一般机电高一些；但仍是项目制生意。",
  "RM17 百万（约 67% 新股所得）用于未来项目的营运资金和履约保证金，典型的“接大工程要先垫钱”。",
  ["订单余额（order book）","再生能源项目政策（如大型太阳能招标）","应收账款与现金流","毛利率"],
  "两条增长线（再生能源、数据中心）都有政策和投资热潮支撑，但承包商盈利波动大，现金流是关键。",
  ["押对趋势很重要：再生能源和数据中心都是长期题材。","项目越大，越要准备好保证金和现金缓冲。"],
  [("项目执行与成本超支","工程延误或材料涨价会吃掉利润。","inference"),("政策依赖","再生能源业务受政府招标节奏影响。","inference"),("财务资料尚未收录","本站未有收入与利润资料。","unknown")])})

u = T+"2026/01/05/ace-market-bound-ghs-holdings-to-raise-rm30mil-from-ipo"
out.append({"slug":"guan-huat-seng","name":"Guan Huat Seng Holdings Bhd","name_zh":"GHS（源发成）","sector_zh":"消费 · 食品制造","one_liner":"马六甲的食品制造商，产品在本地分销贸易渠道销售。",
 "facts":{"market":F("ACE",u),"business":F("马六甲食品制造商，业务属于马来西亚食品与饮料分销贸易行业；计划扩大产品种类、加强与现有客户的关系，并开拓国内外新市场。",u),"issue_price_rm":F(0.25,u),"new_shares":F(120000000,u),"ofs_shares":F(21000000,u),"proceeds_rm":F(30000000,u,"公开发售新股所得"),"market_cap_rm":F(118380000,u),"enlarged_shares":F(473500000,u),
  "prospectus_date":F("2026-01-05",u),"app_open":F("2026-01-05",u),"app_close":F("2026-01-09",u),"listing_date":F("2026-01-22",u,"文章发布时为预定上市日"),"adviser":F("TA Securities Holdings Bhd（主要顾问、保荐人、包销商及配售代理）",u)},
 "use_of_proceeds":U([("马六甲 Batu Berendam 新综合厂区（部分）",12000000),("Krubong 新设施（部分）",9000000),("营运资金",3000000),("营销费用",1500000),("上市费用",4500000)],u),
 "quotes":[{"who":"Yeo Tien Ee，董事经理","text":"Our growth strategy is grounded in discipline, practicality, and a clear understanding of our strengths","src":u}],
 "source_meta":{u:{"title":"ACE Market-bound GHS Holdings to raise RM30mil from IPO","publisher":"The Star","date":"2026-01-05"}},
 "todo_official":"待补：Bursa 上市公告与招股书链接。中文名“源发成”为本站音译，未经公司确认。",
 "analysis":A("GHS 是马六甲的食品厂，钱大部分拿去盖新厂。食品业门槛不高，但做得久、有渠道，就是一门稳生意。",
  [("经销商、零售商与贸易渠道（新闻提及分销贸易行业）。","inference"),("稳定供货与产品种类，具体卖点新闻未说明。","unknown"),("通过分销贸易渠道铺货。","fact"),("与现有客户长期合作，并计划加强关系。","fact"),("食品销售收入；产品与数字未披露。","inference"),("马六甲厂房，新建 Batu Berendam 与 Krubong 设施。","fact"),("食品生产、包装、分销。","inference"),("经销商、原料供应商。","inference"),("原料、人工、厂房折旧；募资 RM1.5 百万做营销。","inference")],
  "食品制造护城河通常来自品牌与渠道；新闻资料不足以判断 GHS 的品牌力。",
  "RM21 百万（70%）投入两个新厂区，属于产能扩张型 IPO。",
  ["新厂投产时间与产能利用率","出口市场进展","原料成本","毛利率"],
  "以 IPO 价算市值约 RM1.18 亿；没有盈利数字前难以判断估值，要读招股书。",
  ["家族食品厂上市，最大的转变是要习惯公开交代每一季成绩。","扩产前先想清楚渠道能不能消化新产能。"],
  [("产能扩张风险","新厂若需求跟不上，折旧会拖累盈利。","inference"),("原料价格","面粉、食油、糖等原料价格波动。","inference"),("财务资料尚未收录","本站未有收入与利润资料。","unknown")])})

pathlib.Path(__file__).with_name("batch2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out))
