
import logging
import re
import os
import json
import argparse

import shutil
from tools.Json import Json

from MyPrompt import *
from QwenApi import QwenApi
from ImageAugment import ImageAugment

from CorpusBuilder import *
from Test import Test

# Set OpenAI's API key and API base to use vLLM's API server.

logging.basicConfig(
    filename='xiolift_trainer.log',              # 日志文件名
    filemode='a',                      # 追加模式 ('w' 为覆盖)
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    level=logging.INFO                 # 记录级别
)


parser = argparse.ArgumentParser(description="示例：添加命令行参数")
parser.add_argument("--task", type=str, required=False, help="test")
parser.add_argument("--flag", type=str, required=False, help="flag")
args = parser.parse_args()

if args.flag == '49':
    ip = '172.16.2.49'

elif args.flag == '35':
    ip = '172.16.2.35'

else:
    ip = '127.0.0.1'


openai_api_base = f"http://{ip}:8002/v1"


class MyTrainer:

    def __init__(self, img_dir, info_dir):

        self.cwd = os.getcwd()

        self.img_dir = img_dir
        self.info_dir = info_dir
        
        self.full_img_path = f'{self.cwd}/{img_dir}'
        self.full_info_path = f'{self.cwd}/{info_dir}'

        self.info_file = f'{self.full_info_path}/info.json'
        self.type_2_images_file = f'{self.full_info_path}/type_2_images.json'
        self.desc_structure_file = f'{self.full_info_path}/desc_structure.json'

        self.qwen_api = QwenApi()
        self.local_qwen_api = QwenApi(base_url=openai_api_base)

    @property
    def key_2_id(self):
        return {key: str(idx + 1) for idx, key in enumerate(self.info)}

    @property
    def id_2_key(self):
        return {str(idx + 1): key for idx, key in enumerate(self.info)}

    @property
    def type_2_images(self):
        return self.build_type_2_images()

    @property
    def relation(self):
        return Json.load(f'{self.full_info_path}/infos.json')

    @property
    def types(self):
        return ','.join(list(self.type_2_images.keys()))

    @property
    def info(self):
        return Json.load(self.info_file)

    def dir_to_dict(self, path):
        result = {}
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                result[item] = self.dir_to_dict(full_path)
            else:
                # 当前目录就是叶子目录，直接用目录名映射文件名列表
                return sorted(os.listdir(path))

        return result

    def build_type_2_images(self):

        if os.path.exists(self.type_2_images_file):
            return Json.load(self.type_2_images_file)

        else:
            type_2_images = self.dir_to_dict(self.full_img_path)
            Json.save(self.type_2_images_file, type_2_images)

        print(json.dumps(type_2_images, indent=2, ensure_ascii=False))
        return type_2_images

    def build_desc_structure(self):

        if os.path.exists(self.desc_structure_file):
            return Json.load(self.desc_structure_file)

        structure = self.build_type_2_images()

        desc_structure = {}

        for type_, images in structure.items():

            l = []
            for image in images:
                path_ = os.path.join(self.full_img_path, type_, image)

                l.append(
                    {
                        'name': image,
                        # 'desc': self.call(path_, system_prompt='你是一个图片内容提取器', text_prompt=IMAGE_EXTRACT_PROMPT)
                        'desc': self.qwen_api.image_info(classify=type_, file=path_)
                    }
                )

            desc_structure[type_] = l

        print(json.dumps(structure, indent=2, ensure_ascii=False))

        Json.save(self.desc_structure_file, desc_structure)

        return desc_structure

    def extract_classify(self, content):

        # match = re.search(r"类别为?[：:]\s*【(.+?)】", content)
        match = re.search(r"类别序号[：:]\s*【(.+?)】", content)
        if match:
            return match.group(1)

        else:
            return content

    def check_sample_tokens(self):
        
        from transformers import AutoTokenizer

        # 根据你训练设置中的 Qwen-VL tokenizer 名称替换路径
        tokenizer = AutoTokenizer.from_pretrained("models/Qwen2.5-VL-7B-Instruct", trust_remote_code=True)

        sample =   {
            "messages": [
            {
                "content": "<image>图片是电梯某个部件的照片，有如下类别及对应的描述信息:\n【{'轿顶检修装置轿顶接线箱': '轿顶检修装置含停止、上下行按钮，用于电梯维修控制。接线箱集成电路与按钮，实现安全检修功能。关键特性为操作按钮和电路集成设计。', '对重架': '对重架用于平衡轿厢重量，由多块对重块组成，通过导轨上下移动，确保电梯运行平稳。关键特性为结构强度和配重设计。', '对重反绳轮': '对重反绳轮用于改变钢丝绳方向，由轮体、支架和轴承组成，确保电梯平衡运行，减少摩擦力，提升效率。', '弹性滚动导靴': '弹性滚动导靴由滚轮、弹簧和支架组成，通过弹簧减震，滚轮沿导轨滚动，确保电梯平稳运行，减少摩擦和噪音。', '制动器臂': '制动器臂用于电梯制动，由杠杆、弹簧和电磁组件组成，通过电磁力控制弹簧压力，实现电梯电机的快速停止与释放。', '层门上坎': '层门上坎：安装导轨和滑轮，支撑门扇运行。由金属框架、导轨、滑轮组成，确保门扇平滑启闭，安全可靠。', '层门门扇加强筋': '层门门扇加强筋增强门扇刚性，防止变形。由金属条构成，嵌入门扇内部或表面，确保电梯层门稳定性和安全性。', '油杯': '电梯油杯用于润滑，由壳体和内部油槽组成，定期加油确保机械部件顺畅运行，防止磨损。结构简单，安装于关键运动部位。', '限速器钢丝绳张紧装置': '限速器钢丝绳张紧装置用于保持钢丝绳张力，由张紧轮、配重块和支架组成，通过配重确保钢丝绳始终处于适当张紧状态，保障电梯安全运行。', '轿厢报警按钮': '轿厢报警按钮：圆形设计，带铃铛图标，用于紧急呼叫。按下后激活警报系统，通知外界求助。关键特征为铃铛标志和紧急功能。', '空心导轨连接板': '电梯空心导轨连接板用于固定导轨，由金属板和螺栓组成，通过螺栓紧固实现导轨间的稳定连接，确保电梯运行安全。', '轿顶风机': '轿顶风机用于电梯通风，由风扇、电机和防护网组成，通过电机驱动风扇旋转实现空气流通，确保轿厢内空气清新。', '层门挂板': '层门挂板连接电梯层门与导轨，由金属板、螺栓和钢丝绳组成，确保层门稳定启闭，安全可靠。', '船型打棒撞弓': '船型打棒撞弓用于电梯门安全关闭，由撞杆、弹簧和缓冲器组成，通过机械碰撞实现门锁紧，确保运行安全。', '门电机': '电梯门电机驱动电梯门开关，由电机、齿轮和控制电路组成，通过电能转化为机械能实现门的自动开合。', '制动器打开检测开关': '制动器打开检测开关用于监测电梯制动器状态，由触点、弹簧和外壳组成，通过触点变化检测制动器是否打开，确保安全运行。', '轿壁': '轿壁为电梯内部侧壁，由金属板构成，提供安全防护和美观装饰。垂直安装，无缝连接，确保乘客安全与舒适。', '门锁滚轮': '门锁滚轮用于电梯门开关，由滚轮、轴承和支架组成。滚轮与导轨接触，通过旋转实现门的平滑开合，确保安全可靠运行。', '补偿缆': '补偿缆用于平衡电梯轿厢与对重的重量差，由钢丝绳和链组成，通过滑轮系统工作，确保电梯运行平稳。', '制动器线圈': '制动器线圈为圆柱形，含电磁线圈和铁芯，通电产生磁场，吸引衔铁，实现电梯制动。关键特性：电磁感应原理，控制电梯停止。', '单向弹性滑动导靴': '单向弹性滑动导靴用于电梯导向，由靴衬、弹簧和调整螺栓组成，通过弹簧提供弹力，确保轿厢单向稳定滑动，减少振动。', '油位镜': '油位镜用于监测电梯油箱油位，由透明视窗和金属边框组成，通过观察内部油标判断油量，确保设备正常运行。', '轿厢护脚板': '轿厢护脚板位于电梯门口下方，保护乘客安全。由金属板和固定螺钉组成，防止物品卡入缝隙，确保电梯运行安全。', '门刀': '电梯门刀部件用于开启和关闭层门，由金属刀片、连杆和固定支架组成，通过机械联动实现精准对位与同步动作。', '轿顶检修装置': '轿顶检修装置含停止、上下行按钮，用于电梯维修时控制运行。配急停开关和指示灯，确保安全操作。工作原理为手动控制，独立于正常运行系统。', '导靴': '导靴用于电梯轿厢导向，由靴衬、靴架组成，沿导轨滑动确保运行平稳。关键特性：滑动结构、导轨配合、稳定支撑。', '限速器棘爪': '限速器棘爪：关键部件，与限速器联动，超速时卡住安全钳导轨，紧急制动。由弹簧、棘爪和底座组成，确保电梯安全停运。', '限速器离心重块': '限速器离心重块通过离心力控制电梯速度，由金属块和轴组成，高速旋转时向外扩展，触发安全机制，确保电梯安全运行。', '缓冲器开关': '缓冲器开关用于检测电梯缓冲行程，由外壳、触点和接线端组成，通过机械触发控制电路通断，确保安全运行。', '盘车手轮': '盘车手轮用于手动操作电梯，由手轮和齿轮组成，通过旋转手轮带动电梯曳引机转动，实现电梯的上下移动。关键特性为手动操作、齿轮传动。', '层门紧急开锁装置': '层门紧急开锁装置由锁钩、复位弹簧和操作杆组成，用于手动解锁层门。通过拉动操作杆，释放锁钩，实现紧急开门功能。', '层门被动门扇': '层门被动门扇，与主动门联动，无独立驱动。由门板、导轨和连接件组成，随主动门开关。确保安全通行，结构简洁稳固。', '对重块压紧装置': '对重块压紧装置由螺杆、螺母和压板组成，通过螺母调节螺杆长度，压紧对重块，确保电梯运行稳定。关键特性为可调性和紧固性。', '限速器棘轮': '限速器棘轮用于电梯超速保护，由棘轮、弹簧和销轴组成，通过棘爪与棘轮啮合阻止电梯轿厢超速坠落，确保安全。', '轿厢铭牌': '轿厢铭牌显示楼层、载重（1000kg）、人数（13人）及品牌信息，具禁烟标志。用于指示电梯状态和安全信息。', '承重钢梁': '承重钢梁用于支撑电梯重量，由高强度钢材制成，通过螺栓连接，确保结构稳定性和安全性。关键特性包括坚固性、连接可靠性和承载能力。', '固定式滑动导靴': '固定式滑动导靴用于电梯轿厢导向，由靴衬、靴架和调整螺栓组成，通过靴衬在导轨上滑动，确保轿厢平稳运行。', '轿厢护栏': '轿厢护栏功能为安全防护，组成包括横杆、立柱和连接件，工作原理为固定在轿厢顶部，防止人员坠落。结构稳固，设计简洁。', '轿厢吊顶': '轿厢吊顶功能为照明与装饰，由灯带、灯具和吸音板组成，工作原理为电能转化为光能，提供均匀光线并吸收噪音。', '制动衬': '电梯制动衬用于制动器，通过摩擦力实现电梯停止。由摩擦材料和金属背板组成，工作时与制动轮接触，产生制动力。关键特性为摩擦性能和耐磨损性。', '门机变频器': '门机变频器控制电梯门开关，含电源、信号输入输出接口，通过变频技术调节电机速度，确保门平稳启停。', '制动器衔铁': '制动器衔铁关键特性：与电磁铁配合，通过磁力吸引实现制动释放；由衔铁、螺栓和弹簧组成，确保电梯安全停止。', '减速箱放油口': '减速箱放油口用于排放减速箱内润滑油，由螺塞和密封圈组成，确保润滑系统清洁，维护设备正常运行。', '曳引机减震垫': '曳引机减震垫用于减少电梯运行时的震动和噪音，由橡胶或类似材料制成，安装于曳引机与基座间，通过弹性变形吸收震动。', '电磁直推鼓式制动器': '电磁直推鼓式制动器用于电梯安全停顿，由电磁线圈、制动臂和弹簧组成，通电时电磁力释放制动，断电时弹簧自动制动，确保安全。', '应急照明': '应急照明部件嵌入式设计，内置LED灯源，确保断电时自动启动，提供持续照明，保障安全疏散。', '制动鼓': '制动鼓为电梯制动系统核心，由轮毂、螺栓组成，通过摩擦力实现制动。工作时，制动器夹紧鼓体，阻止旋转，确保电梯安全停运。', '钳盘式制动器': '钳盘式制动器通过弹簧力使制动钳夹紧制动盘，实现电梯停止。由制动钳、制动盘和弹簧组成，确保安全停梯。', '防托槽机构': '防托槽机构用于防止电梯轿厢或对重脱轨，由导轨、滚轮和支架组成，通过滚轮与导轨紧密配合，确保运行稳定。', '松闸扳手': '松闸扳手用于紧急情况下手动释放电梯制动器。由杆体和连接件组成，通过机械力克服弹簧压力，实现制动器松开，确保安全救援。', '中分门': '中分门由左右两扇门组成，通过电机驱动同步开合，实现乘客进出。关键特性包括对称设计、同步机制和安全触板。', '全盘式制动器': '全盘式制动器用于电梯安全停机，由电磁铁、弹簧和摩擦片组成，通过电磁力释放或弹簧力制动，确保电梯稳定停止。', '导轨凹凸榫头': '导轨凹凸榫头用于电梯导轨连接，确保导轨平顺对接。由金属制成，具有凹凸结构，通过嵌合实现稳固连接，保障电梯运行安全。', '对重块': '电梯对重块用于平衡轿厢重量，由多块金属块组成，通过滑轮系统与轿厢相连，减轻电机负担，确保运行平稳。', '固定式滚动导靴': '固定式滚动导靴用于电梯导向，由轮子、支架和紧固件组成，通过轮子沿导轨滚动实现平稳运行，确保电梯垂直移动的稳定性。', '对重块加托': '对重块加托用于平衡电梯轿厢重量，由金属框架和连接螺栓组成，通过固定对重块实现稳定运行，确保电梯安全高效工作。', '限速器夹绳块': '限速器夹绳块用于电梯超速时夹紧钢丝绳，阻止轿厢移动。由夹持块和弹簧组成，通过弹簧力实现夹紧功能，确保安全停梯。', '限速器开关': '限速器开关用于电梯超速保护，由开关、弹簧和触发机构组成。当电梯速度异常时，触发开关切断电源，确保安全。关键特性为自动检测与紧急制动功能。', '曳引机': '曳引机为电梯提供动力，由电动机、减速器和制动器组成，通过钢丝绳带动轿厢升降，实现垂直运输功能。', '层门主动门扇': '层门主动门扇：带动从动门扇开启，由门扇、导轨、滑轮和连接装置组成，通过钢丝绳传动实现开关动作。', '导轨支架': '导轨支架固定电梯导轨，由金属板和螺栓组成，通过螺栓与墙体连接，确保导轨稳定，支撑电梯运行。', '随性电缆': '随行电缆用于电梯轿厢与固定设备间信号和电力传输，由多股电线组成，随轿厢移动而弯曲，确保稳定连接。', '限速器': '限速器通过弹簧和离心力控制电梯速度，超速时触发安全钳制动。关键组件包括弹簧、轮盘、拉绳和电气开关。', '空心导轨': '电梯空心导轨为金属结构，用于支撑和导向轿厢或对重。表面光滑，有密封条防尘防水，确保运行平稳安全。', '蓄能型缓冲器': '蓄能型缓冲器用于电梯安全，吸收冲击能量。由弹簧和底座组成，通过弹簧压缩实现缓冲，保护乘客和设备安全。', '曳引轮防脱槽机构': '曳引轮防脱槽机构防止钢丝绳脱槽，由导轨和限位装置组成，确保钢丝绳稳定运行，避免事故。', '层门导向轮': '层门导向轮由轮子和轴组成，安装在导轨上，通过滚动引导层门平稳移动，确保开关门顺畅，关键在于其滚动导向功能。', '减速箱': '电梯减速箱关键特性：实现电机与曳引轮速度匹配，由齿轮组、箱体、轴承组成，通过齿轮传动降低转速，增加扭矩。', '积油盒': '积油盒用于收集电梯导轨润滑油脂，防止外溢。由多个方形槽组成，安装于导轨底部，通过槽体汇集并储存润滑油。', '轿厢照明': '轿厢照明功能为提供内部照明，组成包括LED灯源和反光板，工作原理为LED发光经反光板反射，增强亮度，确保轿厢内明亮。', '制动器': '电梯制动器关键特性：用于紧急停止，由电磁组件、弹簧和制动臂组成，通过电磁力与弹簧力控制制动盘，确保安全停梯。', 'T型导轨': 'T型导轨用于电梯轿厢和对重的导向，由T型钢和滑动导靴组成，确保运行平稳。表面光滑，耐磨性强，结构坚固，保证电梯安全高效运行。', '轿厢地坎': '轿厢地坎为电梯门框底部，由金属制成，确保门平稳开关，与层站地坎对接，防止缝隙过大，保障乘客安全进出。', '耗能型缓冲器': '耗能型缓冲器用于电梯安全，吸收冲击能量。由液压缸、活塞和弹簧组成，通过液体压缩耗能，确保电梯平稳停止。', '制动器销轴': '制动器销轴连接制动臂，传递力矩，确保制动器稳定工作。关键特性：圆柱形结构，表面光滑，安装于制动臂孔内，实现旋转与固定功能。', '层门上坎应急导向装置': '层门上坎应急导向装置，含导向槽和固定孔，确保电梯门在紧急情况下顺畅滑动，由塑料制成，结构稳固，安装便捷。', '轿厢操纵箱': '轿厢操纵箱含楼层按钮，用于选择目标楼层。由按钮、指示灯组成，按下相应按钮，电梯控制系统启动运行至指定楼层。', '制动臂鼓式制动器': '制动臂鼓式制动器用于电梯紧急制动，由制动臂、弹簧和电磁铁组成，通过电磁力控制弹簧压力实现制动与释放。', '制动器弹簧': '制动器弹簧用于电梯制动，由弹簧、螺母和垫圈组成，通过弹簧力实现制动功能，确保电梯安全停止。', 'T型导轨连接板': 'T型导轨连接板用于电梯导轨的稳固连接，由金属板和螺栓组成，通过螺栓紧固实现导轨间的稳定链接，确保电梯运行安全。', '导轨压板': '导轨压板用于固定电梯导轨，由金属制成，通过螺栓紧固。其功能是确保导轨稳定，防止位移，保障电梯运行安全。', '层门上导向装置': '层门上导向装置用于引导层门稳定运行，由导向轨、滑轮和固定支架组成，确保门体沿预定轨迹移动，保障电梯安全运行。', '光幕': '电梯光幕由发射和接收装置组成，通过红外线检测障碍物，确保安全。关键特性：非接触式感应，实时监测，防止夹伤。', '减速箱注油口': '减速箱注油口用于添加润滑油，由螺栓和盖板组成，确保密封性，防止漏油，维护减速箱正常运行。', '轿厢门楣': '轿厢门楣连接轿厢与层门，由金属框架和滑动装置组成，确保门平稳开关，防止夹人，保障安全通行。', '轿底减震垫': '轿底减震垫用于吸收电梯运行时的震动，由弹簧和橡胶组成，通过螺栓固定，减少冲击力，确保运行平稳。', '曳引机底座': '曳引机底座支撑曳引机，由金属框架和减震垫组成，确保稳定性和减震效果，连接电梯主机与建筑结构，保障运行安全。', '门锁滚轮门球': '门锁滚轮门球用于电梯门锁系统，由滚轮和轴组成，通过滚轮与门导轨接触，实现门的顺畅开合，确保安全锁定。', '轿厢踢脚板': '轿厢踢脚板保护轿厢底部，防止碰撞损伤。由金属或复合材料制成，安装于轿厢底边，表面平整，耐磨损，确保乘客安全。', '层门限位轮': '层门限位轮由轮体、轴承和固定螺母组成，用于限制电梯层门的开启位置，确保安全运行。通过与导轨配合，实现精准定位和导向功能。', '悬臂式限速器张紧装置': '悬臂式限速器张紧装置用于电梯安全，含张紧轮、配重块和支架。通过配重保持限速器钢丝绳张力，确保限速器正常工作，防止电梯超速。', '曳引轮': '曳引轮通过钢丝绳与轿厢连接，实现升降功能。由轮毂、轮缘和绳槽组成，通过电动机驱动旋转，带动钢丝绳移动，确保电梯安全运行。', '层门门锁电气触电': '层门门锁电气触点：检测门锁状态，由触点、弹簧、接线端子组成，通过电路通断确保电梯安全运行。', '层门门锁机械锁钩': '层门门锁机械锁钩用于电梯层门锁定，由锁钩、弹簧、螺栓组成，通过机械啮合确保门关闭时的安全锁定。', '限速器夹绳块弹簧': '限速器夹绳块弹簧用于电梯安全，通过弹簧力控制夹绳块动作，防止超速。由弹簧、螺母和夹绳块组成，弹簧变形提供夹紧力。', '导向轮': '导向轮用于引导钢丝绳，确保其正确路径。由金属轮毂和多槽轮缘组成，通过槽与钢丝绳配合，实现稳定运行和方向控制。', '旁开门': '旁开门由门扇、导轨、滑轮组成，横向滑动开启，用于电梯层站与轿厢间隔离与通行，确保安全进出。'}】\n请依据图片信息及各类别的描述信息，区别当前图片属于哪个类别，先对图片进行描述，再输出类别。 格式如下:\n描述:【xxx】,\n此描述信息最匹配的类别:【yyy】\n",
                "role": "user"
            },
            {
                "content": "描述:【这张图片展示了一个黄色的控制面板，面板上有多个按钮和指示灯。面板上有一个圆形的旋钮，旁边有多个不同颜色的按钮，可能用于控制设备的不同功能。面板上还挂有一个透明的塑料袋，可能是用于存放工具或配件。面板下方有一个红色的警告标志，提示用户注意安全。整体来看，这个控制面板可能属于某种工业设备或机械，用于操作和控制设备的运行状态。】,\n此描述信息最匹配的类别:【轿顶检修装置轿顶接线箱】\n",
                "role": "assistant"
            }
            ],
            "images": [
                "tests/lsj/xiolift_img_aug/轿顶检修装置轿顶接线箱/s03_轿顶检修装置轿顶接线箱.jpg"
            ]
        }

        text = sample["messages"][0]["content"] + "\n" + sample["messages"][1]["content"]

        # 编码并统计
        tokens = tokenizer.encode(text)
        print("Total tokens:", len(tokens))
        
    def format_new_corpus(self):

        # 设置你的根目录路径
        root_dir = f'{self.cwd}/tests/lsj/部件识别'  # 修改为你的实际路径
        output_dir = f'{self.cwd}/tests/lsj/xiolift_img'   # 分类保存的输出路径

        # 正则匹配去掉 (2) 之类的序号，提取类别名
        def extract_category(filename):
            return re.sub(r'\s*\(\d+\)', '', filename)

        # 遍历根目录
        for folder_name in os.listdir(root_dir):
            folder_path = os.path.join(root_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue  # 忽略非目录

            for file in os.listdir(folder_path):
                if not file.lower().endswith('.jpg'):
                    continue
                category = extract_category(os.path.splitext(file)[0])
                category_dir = os.path.join(output_dir, category)

                os.makedirs(category_dir, exist_ok=True)

                src_file = os.path.join(folder_path, file)
                dst_filename = f"{folder_name}_{file}"
                dst_file = os.path.join(category_dir, dst_filename)

                shutil.copy2(src_file, dst_file)  # 或 shutil.move(src_file, dst_file) 进行移动
                print(f"复制: {src_file} -> {dst_file}")

    def extract_classify_info(self):

        for classify, files in self.type_2_images.items():

            try:
                files = [os.path.join(self.full_img_path, classify, file) for file in files]

                desc = self.qwen_api.classify_info(classify, files)

                logging.info(f'Extracted info for {classify}: {desc}')

                self.info[classify] = desc

            except Exception as e:
                self.info[classify] = 'None'
            
        Json.save(self.info_file, self.info)

    def augment(self):

        """
        图像增强
        """

        input_dir = f'{self.cwd}/xiolift/xiolift_img'
        output_dir = f'{self.cwd}/xiolift/xiolift_img_aug'

        target_num_per_class = 6
        
        aug = ImageAugment(input_dir, output_dir, target_num_per_class)
        aug.augment()


if __name__ == '__main__':

    trainer = MyTrainer('xiolift/xiolift_img_aug', 'xiolift/infos')

    if args.task == 'test':

        Test().test(
            id_to_key=trainer.id_2_key, 
            key_to_id=trainer.key_2_id, 
            structure=trainer.type_2_images, 
            full_img_path=trainer.full_img_path,
            local_qwen_api=trainer.local_qwen_api
        )

    if args.task == 'format_new_corpus':
        # xiolift.format_new_corpus()
        pass

    if args.task == 'extract_classify_info':
        trainer.extract_classify_info()

    if args.task == 'build_xiolift_sft':
        desc_structure = trainer.build_desc_structure()
        CorpusBuilder(trainer.img_dir).build_sft(desc_structure=desc_structure)

    if args.task == 'build_generate_xiolift_sft':

        CorpusGenerator().build_sft(
            trainer.cwd,
            trainer.img_dir,
            trainer.type_2_images, 
            trainer.relation
        )

    if args.task == 'build_xiolift_dpo':
        desc_structure = trainer.build_desc_structure()
        CorpusBuilder().build_dpo(desc_structure=desc_structure)

    if args.task == 'build_desc_structure':
        trainer.build_desc_structure()

    if args.task == 'augment':
        trainer.augment()
