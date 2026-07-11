SAMPLE_WORDS = [
    ("ability", "能力；才能；本领"), ("able", "能够的；有能力的"),
    ("about", "关于；大约；周围"), ("above", "在上面；超过；上述的"),
    ("absolute", "绝对的；完全的"), ("abstract", "抽象的；抽象；摘要"),
    ("academic", "学术的；学业的；学院的"), ("accept", "接受；同意；承认"),
    ("access", "访问；进入；通道；使用权"), ("accident", "事故；意外"),
    ("account", "账户；账号；账目；说明"), ("accurate", "准确的；精确的"),
    ("achieve", "实现；达到；完成；成功"), ("acquire", "获得；取得；学到"),
    ("act", "行动；表演；行为；法案"), ("action", "行动；行为；作用"),
    ("active", "积极的；活跃的；主动的"), ("activity", "活动；行动"),
    ("adapt", "适应；改编；调整"), ("add", "增加；添加；补充说"),
    ("address", "地址；演说；处理；称呼"), ("admire", "钦佩；欣赏；赞赏"),
    ("admit", "承认；准许进入；接纳"), ("advance", "前进；进步；提前"),
    ("advantage", "优点；优势；有利条件"), ("advice", "建议；忠告"),
    ("affect", "影响；使感动"), ("afford", "负担得起；提供；给予"),
    ("agree", "同意；一致；适合"), ("allow", "允许；准许；给予"),
    ("answer", "答案；回答；回应"), ("appear", "出现；似乎；显得"),
    ("apple", "苹果"), ("apply", "申请；应用；适用；涂抹"),
    ("area", "地区；区域；面积；领域"), ("argue", "争论；主张；论证"),
    ("article", "文章；物品；条款"), ("attention", "注意；关注；照料"),
    ("available", "可用的；可获得的；有空的"), ("avoid", "避免；避开"),
    ("balance", "平衡；余额；使平衡"), ("banana", "香蕉"),
    ("bank", "银行；岸；堤"), ("basic", "基本的；基础的"),
    ("bear", "熊；忍受；承担；携带"), ("beat", "击败；敲打；节拍"),
    ("become", "成为；变得；适合"), ("benefit", "利益；好处；受益"),
    ("book", "书；预订；登记"), ("break", "打破；休息；中断；违反"),
    ("bring", "带来；拿来；引起"), ("build", "建造；建立；体格"),
    ("business", "商业；生意；事务；职责"), ("call", "打电话；称呼；呼叫；要求"),
    ("care", "关心；照顾；小心；护理"), ("case", "情况；案例；箱子；案件"),
    ("change", "改变；变化；零钱；更换"), ("charge", "收费；负责；指控；充电"),
    ("check", "检查；核对；支票；阻止"), ("choose", "选择；挑选"),
    ("class", "班级；课程；种类；阶级"), ("clear", "清楚的；清除；晴朗的"),
    ("close", "关闭；接近的；亲密的；结束"), ("complete", "完成；完整的；全部的"),
    ("consider", "考虑；认为；体谅"), ("control", "控制；管理；克制"),
    ("course", "课程；过程；路线；一道菜"), ("create", "创造；创建；引起"),
    ("deal", "处理；交易；大量；协议"), ("develop", "发展；开发；形成"),
    ("difference", "差异；区别；分歧"), ("direct", "直接的；指导；导演；指向"),
    ("draw", "画；拉；吸引；平局"), ("education", "教育；培养；教育学"),
    ("effect", "效果；影响；结果"), ("experience", "经验；经历；体验"),
    ("face", "脸；面对；表面"), ("fail", "失败；未能；不及格"),
    ("field", "田野；领域；场地；字段"), ("figure", "数字；人物；身材；认为"),
    ("find", "找到；发现；认为"), ("form", "形式；表格；形成；组成"),
    ("free", "自由的；免费的；空闲的；释放"), ("get", "得到；到达；变得；理解"),
    ("give", "给；提供；让步；产生"), ("grade", "成绩；年级；等级；评分"),
    ("grape", "葡萄"), ("great", "伟大的；很好的；巨大的"),
    ("ground", "地面；理由；根据；磨碎"), ("hand", "手；帮助；交给；指针"),
    ("head", "头；负责人；前往；领导"), ("hold", "拿着；举行；保持；容纳"),
    ("interest", "兴趣；利益；利息；使感兴趣"), ("issue", "问题；发行；期号；发布"),
    ("language", "语言；措辞；表达方式"), ("last", "最后的；持续；上一个"),
    ("leave", "离开；留下；假期；许可"), ("level", "水平；等级；平坦的"),
    ("light", "光；灯；轻的；点燃"), ("matter", "事情；物质；要紧"),
    ("mean", "意思是；意味着；平均的；吝啬的"), ("notice", "注意；通知；公告"),
    ("orange", "橙子；橘子；橙色"), ("order", "顺序；命令；订单；点菜"),
    ("paper", "纸；论文；试卷；报纸"), ("point", "点；观点；分数；指出"),
    ("practice", "练习；实践；惯例"), ("present", "目前的；出席的；礼物；呈现"),
    ("record", "记录；唱片；录制；成绩"), ("right", "正确的；右边；权利；恰好"),
    ("school", "学校；学院；学派"), ("set", "设置；一套；放置；确定"),
    ("student", "学生；学者"), ("study", "学习；研究；书房"),
    ("subject", "科目；主题；对象；使服从"), ("success", "成功；成就；成功的人"),
    ("take", "拿；带走；花费；接受"), ("teacher", "教师；老师；导师"),
    ("test", "测试；考试；检验"), ("time", "时间；次数；时代；计时"),
    ("train", "火车；训练；培养"), ("use", "使用；用途；利用"),
    ("value", "价值；数值；重视"), ("water", "水；浇水；水域"),
    ("word", "单词；话；消息；措辞"), ("work", "工作；作品；起作用；运转"),
]


def seed_sample_words():
    """Synchronize the bundled offline dictionary without deleting teacher-created words."""
    from models import Word, db

    existing = {item.word: item for item in Word.query.all()}
    changed = False
    for word, meaning in SAMPLE_WORDS:
        item = existing.get(word)
        if item:
            if item.meaning != meaning:
                item.meaning = meaning
                changed = True
        else:
            db.session.add(Word(word=word, meaning=meaning, level="CET4"))
            changed = True
    if changed:
        db.session.commit()


def regrade_existing_answers():
    """Re-evaluate saved answers after the bundled dictionary gains accepted meanings."""
    from models import AnswerRecord, ExamRecord, db
    from services.grading import is_meaning_correct

    attempt_ids = set()
    for answer in AnswerRecord.query.all():
        if not answer.word:
            continue
        answer.correct_answer = answer.word.meaning
        answer.is_correct = is_meaning_correct(answer.user_answer, answer.word.meaning)
        attempt_ids.add(answer.attempt_id)
    for attempt_id in attempt_ids:
        attempt = db.session.get(ExamRecord, attempt_id)
        if not attempt:
            continue
        attempt.correct_count = sum(1 for answer in attempt.answers if answer.is_correct)
        attempt.score = round(attempt.correct_count / attempt.total_questions * 100, 2)
    if attempt_ids:
        db.session.commit()
