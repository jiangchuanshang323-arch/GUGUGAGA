from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'《海洋“发烧”了》全片章节与画面动作规划_v2.docx'
NAVY='174B69'; BLUE='4D8EAA'; PALE='EAF4F5'; CREAM='FFF9EF'; ORANGE='D98260'; INK='304B5A'; MUTED='5F7480'; WHITE='FFFFFF'; LINE='C8DDE1'

chapters=[
 {'name':'片头与第一幕　三地剧情引出同源线索','time':'0:00—1:10','q':'悬念导入：相隔万里的异常，可能由什么共同连接？','target':'让学生先观察真实区域案例，再把注意力收束到赤道中东太平洋；建立“地球会诊”叙事。','evidence':'学生能从三地现象提出“共同线索可能在海洋或大气”的猜想。','shots':[
  ('01','0:00—0:10','海洋为什么会“发烧”','优先直接使用已做好的10秒开场：海面、升温温度计、企鹅少女发出邀请。它承担悬念，不再叠加第二套问题字幕。海面作氛围背景，不把生成画面当作测量证据。','建立“海洋体温”是海温异常的比喻；真正的判读要回到指定海域的观测数据。','使用挥手问好01，站在画面左下约20%宽的位置，先面向镜头，再把教尺/小翅膀指向画面右侧温度计。转入正文时从左下稳住，不要突然换边。','沿用开场原声画面和角色；“咕咕嘎嘎！快来看看海洋为什么会发烧吧！”结束后接约0.3秒柔和水下转场。'),
  ('02','0:10—0:22','给“海洋发烧”命名并落下课程标题','在温度计红色液柱或海温波纹上做短暂放大，转入清爽手绘标题卡；标题下用细字写“追踪一场超强厄尔尼诺的环境多米诺”。','把拟人化悬念转成课程对象：厄尔尼诺及海—气相互作用；标题不暗示全球变暖本身就是厄尔尼诺。','企鹅留在左下三分之一，先惊讶，再切03常态解说；标题放右侧/中上部，角色不压住主标题。','仅显示课程名和一条短副标题。开场与主课底色、线条和配色统一。'),
  ('03','0:22—0:40','秘鲁、印度尼西亚与江南的三组剧情','三联画分别使用秘鲁渔港/渔获新闻实拍、印尼或周边烟霾卫星/新闻实拍、江南暴雨积水新闻实拍。保留时间、地点与来源说明；三张图同尺寸、同一手绘圆角边框。','真实案例用于呈现不同区域的旱、涝、渔业异常；照片是现象证据，不单独证明它们由同一次厄尔尼诺造成。','企鹅缩至左下约18%宽，动作09托腮观察，视线依次转向三张案例卡；不要站在照片中央遮挡证据。','按“秘鲁渔港→印尼烟霾/干旱→江南积水”顺序逐张亮起。图下简短地名和现象；新闻图注明媒体/作者、日期、链接或授权。'),
  ('04','0:40—1:10','把三地异常连回赤道太平洋','直接采用教材或权威机构发布的世界/太平洋地图，不自绘底图。可在原图上叠加透明连线与Niño3.4高亮框；保留图名、图例、比例/经纬度与来源。','提出遥相关问题而暂不提前讲完机制：相隔很远的气候异常可能存在共同海—气背景，但各地影响仍需分区域解释。','地图占画面至少75%，密集标注时全屏；企鹅缩为左下角10%—15%宽画中画或暂时退出，避免缩小地图字体。气泡移至人物旁空白处。','呈现问题“相隔上万公里，它们可能有什么联系？”停半拍，再出现“同一条线索？”作为第二幕钩子。'),
 ]},
 {'name':'第二幕　测体征','time':'1:10—2:20','q':'Q1：海洋怎么“发烧”了？烧到多少度算“超强”？','target':'定位Niño3.4区，读海温距平与滑动平均，区分指数、判据和强度等级。','evidence':'学生能在图上定位区域并说明读数依据；互动①回答0.5℃为何值得关注。','shots':[
  ('05','1:10—1:30','找到气候学家的“体温计”','地图底图直接取自高中地理教材或国家气象/海洋机构的正式出版图，不自绘地图、不用AI生成地图。可叠加透明Niño3.4区框（170°W—120°W、5°N—5°S）和标签。地图放至画面75%—85%，保留原图标题、图例、经纬度与出处；字仍小时切成全屏太平洋放大页。','海温距平是相对常年平均的偏差；明确区域范围，不把整个太平洋平均温度当判据。持续时间与判据按Word所引国家标准口径表达。','讲地图时企鹅缩为左下10%—15%宽小窗或退出，只在地图外沿以教尺/指示线点出区域；气泡也缩短、放到不遮图例的位置。','依次出现“区域→距平→时间条件”。突出区域框时只做透明覆盖标记，地图地形和原有注记保持原样。'),
  ('06','1:30—2:00','读本年度海温距平变化','柱状图采用精致的2.5D层次：柱体正面/侧面明暗分层、柔和短投影、深海蓝与珊瑚橙重点色、少量细网格和清楚的数值标签；滑动平均线另行叠加。','逐月距平与判定用的滑动平均不是同一个量。图例分开，读数口径一致。可加立体质感，但坐标轴、柱高比例和数值关系必须准确，不用透视拉伸造成视觉误判。','讲图时企鹅缩至左下10%—15%宽小窗，用教尺逐点指柱，末尾切08推眼镜；柱图占画面75%以上。数据标签置柱顶，不能被气泡遮挡。','突出“读数—计算/平均—判级”三步。源Word内实时数值在正式录制前重新核验并更新。画面做丰富但不叠加装饰性粒子、玻璃反射或霓虹。'),
  ('07','2:00—2:20','和历史事件比较，留下强度印象','沿用06镜的立体柱图设计，横向对比Word列出的历史峰值；当前预测用虚线空心柱，并在图例中写清“预测/机构/发布时间”。正面柱高按数据线性对应，侧面仅增加质感。','历史观测值与未来预测值证据等级不同，使用实柱与虚线区分；不同机构指数口径不能直接混排。','角色移至左下10%—15%宽小窗，指向最高柱；柱图占画面75%以上，气泡移到无数据的空白上沿。','只保留少量可比数据。实时预测、峰值和“可能刷新纪录”等语句在交片前按最新官方通报复核。'),
  ('08','2:20（互动①，留白约3秒）','互动①：0.5℃听起来很小，为什么科学家紧张？','画面由柱图转成简明海洋热量示意：同样温升下，海洋因水量大、比热容高而对应大量热量变化；数字量级若出现须有计算/来源注。','引出海水热容量与能量观，避免只用“0.5度很小”做直觉推理；不把量级图当作精确直接测量。','切09托腮思考，企鹅在左下，问题卡占右侧；暂停时角色保持托腮，倒计时/留白约3秒，再用11握拳鼓励进入机制段。','按Word所列互动①设置真实停顿。把留白纳入该段节奏，不另行拉长片长。'),
 ]},
 {'name':'第三幕　查病因','time':'2:20—4:00','q':'Q2：谁让海洋发了烧？','target':'用正常态与异常态对比拆解信风、暖水、上升流和沃克环流的因果链，呈现正反馈。','evidence':'学生能补画因果箭头，说明信风减弱后西太平洋偏干、东太平洋偏湿的方向变化。','shots':[
  ('09','2:20—2:50','先看太平洋的“健康状态”','优先直接采用教材/官方机构发布的赤道太平洋剖面图；不另造地图底图。保留原图上西暖池与东部上升流位置，仅叠加解释箭头/标签。暖水表现为沿海面横向铺展的连续层带，边界自然起伏、有清晰薄边和柔和层次；冷水在下方呈深蓝绿连续层，温跃层略有棱线但不做圆贴纸/三角块。云团画在暖水上方的对流区。若用生成工具做动效，只让连续水层轻微流动、边缘缓慢起伏；官方剖面位置、箭头和标签保持锁定，不重生成科学要素。','正常态：东风信风（赤道低层东风）由东向西，推动表层暖水向西；东部冷水上涌；暖池上方上升对流、东侧下沉，共同维持沃克环流。图中明确标出风向和层位。','剖面图占画面75%以上；讲方向时企鹅缩至左下10%—15%宽或暂时退出，05教尺预备后06依次指暖池和上升流。','保持图形有手绘感，但每层仍沿同一海面剖面连续展开；云朵表示对流云，不随意贴在水层边缘。图注引用所用教材/官方图名和页码。'),
  ('10','2:50—3:15','把闭合环流画出来','沿用同一张剖面图，叠加一个清楚闭合的沃克环流箭头，金色只做局部强调，不用霓虹/未来UI。','沃克环流是热带太平洋东西向的纬向环流；让学生看见海面风、垂直运动和降水带是一套相连系统。','企鹅留左侧，07敲击板书在“沃克环流”标签出现时轻敲一次；不要在图中央遮住闭合箭头。','用“风—海温—垂直运动”三个图例颜色；动画遵循箭头先后关系。'),
  ('11','3:15—3:45','异常态：暖水向东扩展，环流减弱','同一官方/教材剖面上做正常→异常过渡：连续暖水层边界向东移动并自然起伏，冷水层/温跃层轮廓相应变化；上方对流云带跟随暖水区东移。可做细腻的二维水纹与慢速层流，让边缘柔和但有轮廓；不以圆形/三角形色块代表整片水层。若用生成工具，只生成受限的纹理/轻微流动，不让它改写底图、箭头、范围或文字。','正常态低层东风信风减弱；可在部分时段用短暂“西风异常/西风爆发”箭头表示向东的扰动，不能写成“西风信风增强”。暖水东移、东部上升流受抑、沃克环流减弱；反馈链按原理逐步呈现。','剖面图占75%以上；企鹅缩至左下小窗，用06指出暖水东移，循环箭头出现时切08推眼镜；图上风向旁直接标“东风信风减弱”，避免角色遮挡箭头。','用相同底图与色标衔接镜09—12。边缘可用轻微波纹/等温线和柔软云朵丰富质感；不加无因果关系的气泡装饰。'),
  ('12','3:45—4:00','正常年与厄尔尼诺年并排对照','教材/官方剖面图同尺度并排，或左右切屏保持同一底图。逐行对照东风信风、暖水层、东部上升流、沃克环流和降水；图内标签加大。','将机制收束为可比较证据，突出海洋异常会带动大气响应；暖/冷水层是沿剖面延伸的连续区域，不是独立几何图标。','图表占画面75%以上，企鹅用10%—15%宽小窗先看正常态、再指异常态；内容密集时角色暂时退出。','用“东风信风：正常较强→厄尔尼诺时减弱”的对照字幕；图源与教材版本/页码标注清楚。'),
  ('13','4:00','互动②：先预测印尼和秘鲁的变化','定格官方/教材太平洋图，在原图适当区域叠加印尼、秘鲁位置标签并留问号；地图放大占75%以上，把答案暂时遮挡。','练习从环流异常推到区域降水响应，而不是背“西旱东涝”。答案在第四幕案例图中揭晓。','企鹅缩到左下10%—15%宽小窗或退出；问号和地名不得遮挡地图原注记。','保留暂停推理时间；第四幕揭晓答案时回闪同一张有来源的小地图，形成首尾对应。'),
 ]},
 {'name':'第四幕　追并发症','time':'4:00—6:40','q':'Q3：一场“高烧”为何让全球多地并发症频发？','target':'按参赛文档的多米诺段落组织多要素影响；主题名称和顺序待用户修改确认，再对应案例与图片。','evidence':'互动③配对正确；学生能区分气候影响链与单一灾害归因。','shots':[
  ('14','4:00—4:10','建立多米诺结构（标签待更新）','先保留五张编号A—E的空白圆角图卡。等用户确定主题名称和顺序后，再替换牌面、图标、配图与本幕串词；不把旧分类当定稿。','多米诺表达气候异常可能沿多个地理要素传导；具体分类以用户后续改稿为准，不表示固定单线因果。','企鹅站左下，03解说后用07轻点A牌；五牌沿画面右侧排开，牌面暂不写主题名。','工作稿暂用A—E占位；正式视频删除占位提示，换成用户定稿内容。'),
  ('15','4:10—4:55','多米诺A（暂沿Word原案：水，待替换）','暂存候选：FAO/官方全球旱涝分布图、教材/官方中国雨带图、阿塔卡马花海真实照片。地图直接使用教材或权威机构原图，不自绘底图。','暂存Word原案中的降水带变化与区域旱涝差异；主题名称、讲解重点和案例对应关系待用户确认后重排。','地图占画面75%以上；角色缩成左下10%—15%宽小窗或暂时退出。只在地图边缘指示，不能挡住地名、图例和出处。','图片先作为素材候选，不锁定到“水”主题；花海实拍不能单独证明由某次厄尔尼诺造成。'),
  ('16','4:55—5:25','多米诺B（暂沿Word原案：气，待替换）','暂存候选：海洋—大气热量交换剖面和官方全球温度曲线/报告图；曲线保留坐标、时间与来源。','暂存Word原案中的海洋储热释放与大气温度关系；新分类确认后再决定该知识点是否留在本镜或移位。','图表占主体，企鹅缩成左下小窗；08推眼镜强调限定语。','不提前锁定主题牌标签；如果保留预测语句，核对出处、发布时间和预测属性。'),
  ('17','5:25—5:55','多米诺C（暂沿Word原案：生，待替换）','暂存候选：教材/官方秘鲁上升流剖面、科研机构发布的鳀鱼与珊瑚真实图片；分栏并标地点、日期和来源。','暂存Word原案中的上升流—营养盐—渔业链及珊瑚热压力；未证实同地同期前，不将图片做成前后对照。','图片占右侧大区；企鹅左下用教尺逐项指示，细节需读清时缩小人物或暂时退出。','渔获量和配额数据先不嵌死；若保留，核对IMARPE原始公告及统计口径。'),
  ('18','5:55—6:20','多米诺D（暂沿Word原案：土，待替换）','暂存候选：NASA FIRMS官方火点/遥感图，搭配有明确地点和日期的真实火灾照片；地图底图用官方发布图。','暂存Word原案中的干旱与火险条件；火点和照片说明观测到火灾，不单独证明唯一成因。','地图占画面75%以上，角色缩小；10叉腰提醒用于“风险上升不等于单因果”。','日期、图例和遥感来源须清晰；主题是否保留待用户修改。'),
  ('19','6:20—6:40','多米诺E（暂沿Word原案：碳，待替换）','若此主题最终保留，再选用教材/官方碳循环示意图和NOAA/研究机构序列；当前不制作定稿牌面。','暂存Word原案中的火灾排放与海洋碳汇内容；“估算值”限定语、时间范围与来源必须保留。','若保留此镜，图表占右侧主体，企鹅缩小并用08推眼镜强调估算限定语。','五类主题未确认前，本镜只作内容候选，不与最终时轴、配音和数据画面锁定。'),
  ('20','6:40','互动③：按用户改稿后的主题重新连线','五张牌用A—E占位，案例图标先列素材池；用户确定主题名称和顺序后，再为每项选案例并制作配对关系。','互动目标仍为按证据把案例与地理要素/主题关联；具体类别、答案和反馈以用户定稿为准。','企鹅切09托腮提问，反馈时换12点赞；连线区占画面右侧75%，人物缩至角落。','答案路径暂留空白，不沿用旧稿配对答案；主题定稿后同步更新图卡、旁白和评价证据。'),
 ]},
 {'name':'第五幕　辨析与乡土','time':'6:40—8:00','q':'Q4前半：这是天灾还是人祸？为什么影响会滞后？','target':'辨析自然变率与人为增暖，解释海洋热容量带来的时间滞后，并由全球尺度推到新疆乡土尺度。','evidence':'学生能说出二者不同、可能叠加放大风险；能沿地图定位太平洋—中国—新疆。','shots':[
  ('21','6:40—7:10','厄尔尼诺不是全球变暖的别名','自绘双曲线：一条起伏的自然变率线，一条长期上升背景趋势线；旁边用两张小标签“自然过程”“人为增暖背景”。','概念区分后再谈风险叠加；两条曲线是概念示意，坐标标“示意”且不暗示二者简单算术相加。','企鹅左下，10叉腰提醒“不是同一个概念”，随后03解说；双曲线占中右区域。','保留互动思考空白；讲解将定义、叠加影响和人类责任分成三步。'),
  ('22','7:10—7:35','解释滞后：海洋升温慢，影响可能晚到','横向时间轴对齐“海温变化”和“区域影响”，用缓慢起伏曲线和延后箭头表现滞后；提供历史事件标记时注明事件年份。','水的比热容大，海洋储热与释放较慢；海温峰值和影响峰值不必同步。具体年份、预测月份和“最大影响季节”须按官方资料复核。','企鹅站左下，用09托腮后06指时间轴的“滞后”箭头；图表横跨右侧。','不要把Word中的预测月份做成永久固定动画；可设计可替换时间标签。'),
  ('23','7:35—8:00','从太平洋推近到新疆和石河子','全球→中国→新疆→天山北坡/石河子直接采用教材或自然资源部标准地图逐级切换/放大，不重绘底图、不用AI造地图。最后另切真实绿洲农田照片。','遥相关是远距离区域间的统计联系，不是太平洋海水直接流到新疆；Word所列历史统计和当年风险需注明来源、范围及预测属性。','每一级地图至少占画面75%；密集地名时全屏放大，企鹅缩为角落10%—15%小窗或退出。教尺只在图边定位；所有地名须能在手机屏幕读清。','中国地图标注标准地图图号/审图信息。新疆预测用预测措辞，不把它说成已发生事实。'),
 ]},
 {'name':'第六幕　开处方','time':'8:00—9:00','q':'Q4后半：人类能做什么？','target':'把“早预警、早行动”的适应措施与减排/碳中和的减缓措施区分，并落到学生可行动项目。','evidence':'学生能各举出一项适应和减缓行动；形成家庭预警/应急清单。','shots':[
  ('24','8:00—8:30','处方一：早发现、早预警、早行动','用真实官方监测页面截屏（截取日期和机构）、真实预警短信样式/水库调度照片；个人信息打码，截图不得伪造官方界面。','适应是降低灾害暴露与损失；监测预报提供准备时间，但概率、有效期及确定性应忠实引用当时的官方通报。','企鹅站左侧，08推眼镜转06指预警步骤；画面右侧三张卡依次“监测—预警—行动”。','实时概率和预报必须在最终锁片前刷新；没有把握的百分比不配音、不做大字结论。'),
  ('25','8:30—9:00','处方二：减缓增暖风险，并从身边行动','风电/光伏使用真实高清照片；切到学生关灯、骑行或家庭应急清单实拍/绘制小卡。“适应”和“减缓”用两列。','减缓是控制温室气体排放、限制长期人为增暖；它不能阻止自然厄尔尼诺，但可以降低长期风险背景。个人应急行动属于适应，不与碳中和混为一类。','企鹅先11握拳鼓励，再12点赞；人物放左下，行动清单放右侧，最后面向镜头邀请学生选一项。','留一条可执行任务：关注官方监测、检查家庭应急包或完成一次节能行动；Word中的具体清单可做勾选动画。'),
 ]},
 {'name':'尾声　总结检测','time':'9:00—9:30','q':'回到开头：怎样完整解释海洋“发烧”及其影响？','target':'用机制链总结，检测迁移能力，并预告拉尼娜后续课程。','evidence':'结尾情境题能检查判读、机制、区域影响与应对；答案和评分标准需随片交付。','shots':[
  ('26','9:00—9:15','四步会诊与五主题总收束','四联图标按体温计→沃克环流→五主题多米诺→处方笺依次点亮；底部机制链用短箭头串联。','总结“信风减弱→暖水东移→上升流减弱→沃克环流减弱/错位→全球水热格局改变”；再回扣遥相关、滞后与自然变率/人为增暖辨析。','企鹅回到左下中心位，06指总结链，末句切03常态解说并挥手过渡；保留足够时间读完因果链。','心跳/海浪声收稳；保留首尾相同的体温计图标，让开头问题得到明确回答。'),
  ('27','9:15—9:30','原创情境题与下期预告','全屏简洁试题卡，旁边小缩略图：Niño3.4定位图、机制链、世界影响图。结尾角落出现“下期会诊：拉尼娜”。','参赛Word明确提醒：原包尚未附镜27原创题的材料、设问、答案与评分标准；建议题面覆盖判读、因果推理、区域迁移、应对决策，成片前需补齐。','企鹅站左下约18%宽，11握拳鼓励后18挥手告别；题卡占右侧大区，尾句后再停留2秒便于读题。','不要把提问口播完就立刻切黑；需提供作答停留时间。题目答案/评分量表同步补入03号评价附件。'),
 ]}
]

action_rows=[
 ('01 挥手问好','片头镜01；镜27挥手前可用18告别'),('02—04 常态待机/解说/眨眼','讲授间的短暂待机与轻微表情变化；每段不机械循环'),('05—07 教尺预备/指向/敲击','镜04—07、09—12、15、23、26的图示讲解'),('08 推眼镜泛光','镜05—07、11、16、19、24的判据/结论/风险提示'),('09 托腮思考','镜03、08、13、20、22的观察和互动停顿'),('10 叉腰提醒','镜18、21辨误区和风险说明'),('11—12 握拳/点赞','镜08、20、25、27的答题反馈与鼓励'),('13—15 走位/站稳','片头入场、讲台侧移与章节转场；地图主体出现时不横穿关键图表'),('16—18 鞠躬/起身/挥手','尾声镜27；镜头按鞠躬—停顿—起身—挥手顺序完成'),
]

def shade(cell,color):
    tcPr=cell._tc.get_or_add_tcPr(); shd=tcPr.find(qn('w:shd'))
    if shd is None:shd=OxmlElement('w:shd');tcPr.append(shd)
    shd.set(qn('w:fill'),color)
def borders(table,color=LINE,size='5'):
    tblPr=table._tbl.tblPr; b=tblPr.find(qn('w:tblBorders'))
    if b is None:b=OxmlElement('w:tblBorders');tblPr.append(b)
    for edge in ('top','left','bottom','right','insideH','insideV'):
        e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),size);e.set(qn('w:color'),color);b.append(e)
def set_cell_margins(cell,top=90,start=110,bottom=90,end=110):
    tc=cell._tc;pr=tc.get_or_add_tcPr();mar=pr.first_child_found_in('w:tcMar')
    if mar is None:mar=OxmlElement('w:tcMar');pr.append(mar)
    for k,val in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        node=mar.find(qn('w:'+k))
        if node is None:node=OxmlElement('w:'+k);mar.append(node)
        node.set(qn('w:w'),str(val));node.set(qn('w:type'),'dxa')
def set_repeat_table_header(row):
    pr=row._tr.get_or_add_trPr();el=OxmlElement('w:tblHeader');el.set(qn('w:val'),'true');pr.append(el)
def no_split(row):
    pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
def set_width(cell,inches):cell.width=Inches(inches)
def set_font(run,size=9,bold=False,color=INK,name='Microsoft YaHei'):
    run.font.name=name;run.font.size=Pt(size);run.font.bold=bold;run.font.color.rgb=RGBColor.from_string(color)
    rpr=run._element.get_or_add_rPr();rf=rpr.rFonts
    if rf is None:rf=OxmlElement('w:rFonts');rpr.insert(0,rf)
    for key in ('ascii','hAnsi','eastAsia','cs'):rf.set(qn('w:'+key),name)
def set_para(p,after=3,before=0,line=1.12,keep=False):
    f=p.paragraph_format;f.space_after=Pt(after);f.space_before=Pt(before);f.line_spacing=line
    if keep:f.keep_with_next=True
def add_text(p,text,size=9,bold=False,color=INK):
    r=p.add_run(text);set_font(r,size,bold,color);return r
def add_labeled(cell,label,text):
    p=cell.paragraphs[0];set_para(p,after=2,line=1.12)
    add_text(p,label,8.5,True,BLUE)
    p2=cell.add_paragraph();set_para(p2,after=0,line=1.16);add_text(p2,text,8.6,False,INK)
def add_bullet(doc,text):
    p=doc.add_paragraph(style='List Bullet');set_para(p,after=3,line=1.16);add_text(p,text,9.5)
def add_field(p,code):
    r=p.add_run();begin=OxmlElement('w:fldChar');begin.set(qn('w:fldCharType'),'begin');instr=OxmlElement('w:instrText');instr.set(qn('xml:space'),'preserve');instr.text=code;sep=OxmlElement('w:fldChar');sep.set(qn('w:fldCharType'),'separate');txt=OxmlElement('w:t');txt.text='1';end=OxmlElement('w:fldChar');end.set(qn('w:fldCharType'),'end');r._r.extend([begin,instr,sep,txt,end]);set_font(r,8,False,MUTED)

doc=Document();sec=doc.sections[0];sec.page_width=Inches(8.27);sec.page_height=Inches(11.69);sec.top_margin=Inches(.62);sec.bottom_margin=Inches(.58);sec.left_margin=Inches(.62);sec.right_margin=Inches(.62);sec.header_distance=Inches(.28);sec.footer_distance=Inches(.28)
styles=doc.styles
styles['Normal'].font.name='Microsoft YaHei';styles['Normal'].font.size=Pt(9.5);styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
for name,size,color in [('Title',25,NAVY),('Heading 1',17,NAVY),('Heading 2',13,BLUE),('Heading 3',10.5,INK)]:
    s=styles[name];s.font.name='Microsoft YaHei';s.font.size=Pt(size);s.font.bold=True;s.font.color.rgb=RGBColor.from_string(color);s._element.rPr.rFonts.set(qn('w:eastAsia'),'Microsoft YaHei');s.paragraph_format.keep_with_next=True
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER;add_text(footer,'《海洋“发烧”了》全片章节与画面动作规划  ·  ',8,False,MUTED);add_field(footer,'PAGE')

p=doc.add_paragraph(style='Title');p.alignment=WD_ALIGN_PARAGRAPH.LEFT;set_para(p,after=3,line=1.05);add_text(p,'《海洋“发烧”了》\n全片章节与画面动作规划',25,True,NAVY)
p=doc.add_paragraph();set_para(p,after=9);add_text(p,'依据参赛文档 00—04 与 02 分镜脚本 27 镜展开',11,False,BLUE)
p=doc.add_paragraph();set_para(p,after=8,line=1.25);add_text(p,'规划用途：把现有教学内容转成可拍摄、可找图、可剪辑的分镜执行稿。课程仍按 Word 的约 9 分 30 秒、七个教学环节和四阶问题链组织；每镜标明画面素材、讲解原理、角色动作站位、字幕或互动。',10.2,False,INK)

note=doc.add_table(rows=1,cols=1);note.alignment=WD_TABLE_ALIGNMENT.CENTER;note.autofit=False;set_width(note.cell(0,0),7.03);shade(note.cell(0,0),CREAM);borders(note,ORANGE,'8');set_cell_margins(note.cell(0,0),130,170,130,170)
p=note.cell(0,0).paragraphs[0];set_para(p,after=0,line=1.18);add_text(p,'现有开场的接法  ',10,True,ORANGE);add_text(p,'已完成的 10 秒企鹅开场放在镜 01 的 0:00—0:10，替换 Word 原镜头的氛围镜头；标题镜 02 从 0:10 接入。这样不额外增加片长，也避免重复介绍。',9.3)

doc.add_heading('本轮批注落实',level=1)
for text in [
 '地图改用教材、国家气象/海洋机构或自然资源部正式地图；不自绘底图、不用AI生成地图。只叠加透明区域框、箭头和说明。地图至少占画面75%，细字多时全屏放大，人物缩至角落或暂时退出。',
 '海温柱图加轻微2.5D层次：柱体正面/侧面明暗、柔和投影和分层配色；坐标轴、比例和柱高仍准确，不用透视扭曲数据。',
 '暖池与冷水层改成沿剖面连续铺展、边界自然起伏的层带，边缘清楚且有柔和层次；对流云放在暖水上方对应位置，不用孤立圆形或三角色块代表整层水。',
 '术语写作：正常态东风信风（赤道低层东风）自东向西；厄尔尼诺时东风信风减弱。个别时段可出现西风异常/西风爆发，但不称“西风信风增强”。',
 '多米诺五类名称、排序和答案暂不锁定。旧Word分类只作候选占位，待用户改稿后再同步更换卡片、案例、解说和互动配对。',
]:add_bullet(doc,text)

doc.add_heading('全片章节总览',level=1)
tbl=doc.add_table(rows=1,cols=4);tbl.alignment=WD_TABLE_ALIGNMENT.CENTER;tbl.autofit=False
widths=[1.78,1.22,2.45,1.58]
for c,w in zip(tbl.rows[0].cells,widths):set_width(c,w);shade(c,NAVY);set_cell_margins(c)
for c,t in zip(tbl.rows[0].cells,['章节','时间','要解决的问题','学习证据']):c.text='';p=c.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER;add_text(p,t,8.5,True,WHITE)
set_repeat_table_header(tbl.rows[0])
for ch in chapters:
    row=tbl.add_row();no_split(row)
    vals=[ch['name'].replace('片头与第一幕　','').replace('尾声　',''),ch['time'],ch['q'],ch['evidence']]
    for i,(c,t,w) in enumerate(zip(row.cells,vals,widths)):
        set_width(c,w);set_cell_margins(c,80,100,80,100);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        if len(tbl.rows)%2==0:shade(c,'F4F8F8')
        p=c.paragraphs[0];set_para(p,after=0,line=1.08);add_text(p,t,8.2,i==0,NAVY if i==0 else INK)
borders(tbl)

doc.add_heading('统一画面与角色调度',level=1)
for text in [
 '主画幅按 16:9 设计。水下课堂建立为固定场景。普通讲解时展示板/案例占右侧约65%—72%，企鹅老师在左侧约18%—25%宽。只要出现地图，地图就成为主画面并至少占75%；地名标注密集时全屏/分屏放大，人物缩至10%—15%宽角落小窗或暂时退出，保证手机上地名可读。',
 '气泡固定在角色头部旁边的空白区，尾尖明确指向兜帽；每次只显示当前口播句，逐句替换。正文采用得意黑，两端对齐、末行左对齐，统一字形基线；图表单位/来源标注与角色气泡分开，避免挤进同一框。',
 '科学图表、海温分布、沃克环流、全球影响和中国地图用教材/官方图或按数据自绘，不能用文生图决定箭头、边界、经纬度。案例新闻和珊瑚/渔港/火灾等画面优先用可追溯的高清实拍，标作者/机构、地点、日期和来源；氛围插画不能伪装成新闻证据。',
 '同一知识图贯穿讲解时保持方向、色标和比例一致。正常态与异常态尽量使用同一剖面做动画变换；人物移动只在段落转场发生，讲关键数据时停稳并用教尺定点，不在图表中间来回走。',
]:add_bullet(doc,text)

doc.add_heading('逐镜章节规划',level=1)
for ci,ch in enumerate(chapters,1):
    h=doc.add_heading(ch['name'],level=2);set_para(h,after=4,before=8,keep=True)
    p=doc.add_paragraph();set_para(p,after=5,line=1.12);add_text(p,'时间 ',8.5,True,BLUE);add_text(p,ch['time']+'　',8.5,False,INK);add_text(p,'章节任务 ',8.5,True,BLUE);add_text(p,ch['target'],8.5,False,INK)
    for no,tm,title,visual,principle,pose,overlay in ch['shots']:
        p=doc.add_paragraph(style='Heading 3');set_para(p,after=2,before=4,keep=True);add_text(p,f'镜头 {no}　{tm}　{title}',10.2,True,NAVY)
        card=doc.add_table(rows=2,cols=2);card.alignment=WD_TABLE_ALIGNMENT.CENTER;card.autofit=False
        cwidth=[3.50,3.50]
        for row in card.rows:
            no_split(row)
            for c,w in zip(row.cells,cwidth):set_width(c,w);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP;set_cell_margins(c,75,110,75,110)
        shade(card.cell(0,0),PALE);shade(card.cell(1,1),PALE)
        add_labeled(card.cell(0,0),'画面与图片','')
        # remove the empty second paragraph created by helper for an intentionally compact field
        card.cell(0,0).paragraphs[1].text=visual
        for r in card.cell(0,0).paragraphs[1].runs:set_font(r,8.45,False,INK)
        add_labeled(card.cell(0,1),'讲解原理',principle)
        add_labeled(card.cell(1,0),'角色动作与站位',pose)
        add_labeled(card.cell(1,1),'字幕、互动与剪辑',overlay)
        borders(card)
    p=doc.add_paragraph();set_para(p,after=3,before=3,line=1.12);add_text(p,'本章评价证据  ',8.3,True,ORANGE);add_text(p,ch['evidence'],8.3,False,MUTED)

doc.add_heading('企鹅老师动作调用表',level=1)
p=doc.add_paragraph();set_para(p,after=6);add_text(p,'动作沿用现有 18 张关键姿势素材。关键知识点用动作强调，解释过程回到常态解说；走位控制在章节开头或转场，避免人物持续摆动分散读图。',9.5)
tbl=doc.add_table(rows=1,cols=2);tbl.alignment=WD_TABLE_ALIGNMENT.CENTER;tbl.autofit=False
for c,w in zip(tbl.rows[0].cells,[2.65,4.35]):set_width(c,w);shade(c,NAVY);set_cell_margins(c)
for c,t in zip(tbl.rows[0].cells,['素材编号与动作','主要调用位置']):c.text='';add_text(c.paragraphs[0],t,9,True,WHITE)
set_repeat_table_header(tbl.rows[0])
for i,(action,use) in enumerate(action_rows):
    row=tbl.add_row();no_split(row)
    for j,(c,t,w) in enumerate(zip(row.cells,[action,use],[2.65,4.35])):set_width(c,w);set_cell_margins(c);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;c.text='';set_para(c.paragraphs[0],after=0);add_text(c.paragraphs[0],t,8.7,j==0,INK)
    if i%2==1:
        for c in row.cells:shade(c,'F4F8F8')
borders(tbl)

doc.add_heading('制作前核对清单',level=1)
checks=[
 ('动态图表','海温距平、滑动平均、强度判级、历史峰值和预报数值均按参赛文档选用，但须在最终配音/导出前对照国家气候中心、WMO或文中指定的原始口径重新核实；历史值与预测值用不同线型。'),
 ('来源与地图','逐张记录案例照片的来源、拍摄日期、地点、许可/引用要求。全球影响图引用FAO/官方机构；中国地图使用自然资源部标准地图并标注审图信息。'),
 ('镜27原创题','参赛文档指出：整合包缺少原创新情境题的材料、设问、参考答案和评分标准。当前分镜只规划题面位置与能力点；录制前必须补齐完整题目并与03评价量表对应。'),
 ('语音与节奏','配音约按文档建议的讲解速度录制；互动①—③和结尾题留出真实思考时间。角色口型只在讲解时开合，停顿/聆听时闭合。'),
 ('字幕与画面','每句气泡紧跟口播，末行左齐、尾尖指向角色；图表正文优先保证可读，数据来源放图脚/片尾，不挤入主气泡。每一章复查动作素材身份一致、脚底线稳定、教尺不穿越关键文字。'),
]
for label,body in checks:
    p=doc.add_paragraph();set_para(p,after=5,line=1.16);add_text(p,label+'　',9.3,True,BLUE);add_text(p,body,9.2)

doc.add_heading('资料依据与本规划边界',level=1)
p=doc.add_paragraph();set_para(p,after=4,line=1.16);add_text(p,'课程目标、七个教学环节、四阶问题链、27镜时码、素材纪律与评价证据均从参赛文档 00—04 提取；企鹅动作编号来自项目现有 18 姿势素材包。本文负责画面组织和执行调度，不替代原文知识审查、实时数据更新、图片授权核查或缺失的原创试题。',9.2)
p=doc.add_paragraph();set_para(p,after=2);add_text(p,'参赛文档：',8.3,True,MUTED);add_text(p,'《海洋“发烧”了》微课参赛文档（00—04全套）终稿 v3.0。',8.3,False,MUTED)
p=doc.add_paragraph();set_para(p,after=2,line=1.1);add_text(p,'风向术语核对：',8.1,True,MUTED);add_text(p,'NOAA Climate Prediction Center，ENSO Cycle 与 ENSO FAQ。正常态低层为东风信风；厄尔尼诺发展期东风信风减弱，阶段性西风异常/西风爆发不等于“西风信风增强”。',8.1,False,MUTED)
p=doc.add_paragraph();set_para(p,after=1,line=1.05);add_text(p,'https://cpc.ncep.noaa.gov/products/analysis_monitoring/ensocycle/enso_schem.shtml',7.5,False,BLUE)
p=doc.add_paragraph();set_para(p,after=1,line=1.05);add_text(p,'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ensofaq.shtml',7.5,False,BLUE)
doc.core_properties.title='《海洋“发烧”了》全片章节与画面动作规划'
doc.core_properties.subject='基于参赛文档00—04的微课分镜执行规划'
doc.core_properties.keywords='厄尔尼诺,微课,分镜,动作调度,画面规划'
ROOT.mkdir(parents=True,exist_ok=True);doc.save(OUT);print(OUT)
