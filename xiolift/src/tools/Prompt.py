
from src.tools.Json import Json

class Prompt:

    @staticmethod
    def intent_recognition(f, s):

        prompt = "你现在是AI训练师，负责数据标注工作，请判断用户输入和命中知识中的语句是否有意思一样的，返回正确或者错误。 " \
                 "\n返回示例: " \
                 "\n示例1: " \
                 "\n用户输入: 学分申请成功怎么查看" \
                 "\n命中知识: 查学分" \
                 "\n返回: {\"user_input\": \"学分申请成功怎么查看\",\"ai_hit_correct\": \"错误\"}" \
                 "\n示例2: " \
                 "\n用户输入: 寝室可带热水器吗" \
                 "\n命中知识: 寝室有热水么;住宿是否可携带热水器" \
                 "\n返回: {\"user_input\": \"寝室可带热水器吗\",\"ai_hit_correct\": \"正确\"}" \
                 "\n只需要返回如上示例中的json结构，不要输出解释，不要其他信息"

        return prompt + "\n用户输入: " + f + "\n命中知识: " + s

    @staticmethod
    def build_out_json(input_, flag):
        return '{"user_input": "' + input_ + '","ai_hit_correct": "' + flag + '"}'

    @staticmethod
    def build_infer(match, s, i, flag):

        if flag == '正确':
            return f"推理过程：命中知识【{match}】中【{s}】和用户输入【{i}】意图一致，所以最终回应是"

        else:
            return f"推理过程：命中知识【{match}】中不存在和用户输入【{i}】意图一致的语句，所以最终回应是"

    @staticmethod
    def build_example(idx, match, s, i, flag):

        return f"示例{idx}：\n用户输入：【{i}】\n命中知识：【{match}】\n" \
            + Prompt.build_infer(match=match, s=s, i=i, flag=flag) + '\n' + Prompt.build_out_json(i, flag)

    @staticmethod
    def raft_train(f, s):

        prompt = "你现在是AI训练师，负责数据标注工作，请判断用户输入和命中知识中的语句是否意图一致。\n" \
                 "下面是两个示例：\n" \
                 + Prompt.build_example(1, '查学分', '查学分', '学分申请成功怎么查看', '错误') + '\n' \
                 + Prompt.build_example(2, '寝室有热水么；住宿是否可携带热水器', '住宿是否可携带热水器', '寝室可带热水器吗', '正确') + '\n' \
                 + "请参考上面的示例，给出推理过程和相应的json结构。\n"

        return prompt + f"用户输入：【{f}】\n命中知识：【{s}】"

    @staticmethod
    def raft_infer(match, s, i, flag):
        return Prompt.build_infer(match, s, i, flag) + '\n' + Prompt.build_out_json(i, flag)

    @staticmethod
    def scene_classify_1(f, all, one, two):

        a = '、'.join(all)
        b = '、'.join(one)
        c = '、'.join(two)

        prompt = '你现在是AI训练师，负责数据标注工作，请判断用户输入最适合哪个业务场景，以及业务一级分类和业务二级分类。\n' \
                 f'用户输入：{f}' \
                 f'\n业务场景：{a}' \
                 f'\n业务一级分类：{b}' \
                 f'\n业务二级分类：{c}' \
                 '\n返回示例： { "用户输入": "", "业务场景": "", "业务一级分类": "", "业务二级分类": ""}'

        return prompt

    @staticmethod
    def scene_classify_group(f, scene_group):

        # 场景分类, todo 需要添加未知分类
        ss = []
        for group in scene_group:
            s = '/'.join(group)
            ss.append(s)

        ss = '、'.join(ss)

        prompt = '你现在是AI训练师，负责数据标注工作，请判断用户输入最适合哪个分类组合，将匹配的分类组合按顺序拆分为业务场景，以及业务一级分类和业务二级分类。\n' \
                 f'用户输入：{f} \n' \
                 f'分类组合：{ss} \n' \
                 '返回示例： { "用户输入": "", "业务场景": "", "业务一级分类": "", "业务二级分类": ""}'

        return prompt

    @staticmethod
    def scene_output(f, scene, one, two):

        a = {"用户输入": f, "业务场景": scene, "业务一级分类": one, "业务二级分类": two}
        return Json.json_2_str(a)



"""梦颖提供的最新QA提取的prompt
文档：【】
从图中所提供的信息中概括性的提取重要的问题及该问题的答案
要求如下:
1. 要保证所提取问题和答案的完整性，方便后续检索，对于出现设备型号的地方要带上
2. 问题和答案一定要成对出现
3. 问题要有一定的概括性， 问题的答案不少于50字
4. 对于图中出现的标题可作为问题，标题下的内容可作为答案
5. 提取尽可能多的QA覆盖文档内容。

以QA对的形式返回，如：

问题1： 8642如何调试?
答案: 调试过程为...

问题2： 8642状态查询
答案: 查询方式为...
"""