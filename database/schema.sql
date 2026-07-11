-- WordMaster 数据库初始化脚本
-- 模块1: user 表
-- 模块2: word 表（基础结构，成员B可扩展）
-- 模块3: exam_record, answer_record 表

CREATE DATABASE IF NOT EXISTS wordmaster DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wordmaster;

CREATE TABLE IF NOT EXISTS user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '加密密码',
    nickname VARCHAR(50) COMMENT '昵称',
    email VARCHAR(100) COMMENT '邮箱',
    status TINYINT DEFAULT 1 COMMENT '1-正常 0-禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS word (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    word VARCHAR(100) NOT NULL COMMENT '英文单词',
    meaning VARCHAR(500) NOT NULL COMMENT '中文释义',
    phonetic VARCHAR(100) COMMENT '音标',
    level VARCHAR(20) COMMENT '难度等级',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS exam_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total_questions INT NOT NULL COMMENT '总题数',
    correct_count INT DEFAULT 0 COMMENT '正确题数',
    score DECIMAL(5,2) DEFAULT 0 COMMENT '得分(百分制)',
    status VARCHAR(20) DEFAULT 'in_progress' COMMENT 'in_progress/submitted',
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS answer_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    exam_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    word_id BIGINT NOT NULL,
    user_answer VARCHAR(500) COMMENT '用户答案',
    question_type VARCHAR(30) DEFAULT 'en_to_cn' COMMENT '题目类型',
    is_correct TINYINT DEFAULT 0 COMMENT '是否正确',
    question_order INT COMMENT '题目序号',
    FOREIGN KEY (exam_id) REFERENCES exam_record(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (word_id) REFERENCES word(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 示例单词数据（便于模块3联调测试，成员B可替换为完整词库）
INSERT INTO word (word, meaning, phonetic, level) VALUES
('abandon', '放弃；遗弃', '/əˈbændən/', 'CET4'),
('ability', '能力；才能', '/əˈbɪləti/', 'CET4'),
('absolute', '绝对的；完全的', '/ˈæbsəluːt/', 'CET4'),
('abstract', '抽象的；摘要', '/ˈæbstrækt/', 'CET4'),
('academic', '学术的；学院的', '/ˌækəˈdemɪk/', 'CET4'),
('accept', '接受；承认', '/əkˈsept/', 'CET4'),
('access', '通道；访问', '/ˈækses/', 'CET4'),
('accident', '事故；意外', '/ˈæksɪdənt/', 'CET4'),
('accompany', '陪伴；伴随', '/əˈkʌmpəni/', 'CET4'),
('accomplish', '完成；实现', '/əˈkɑːmplɪʃ/', 'CET4'),
('account', '账户；说明', '/əˈkaʊnt/', 'CET4'),
('accurate', '准确的；精确的', '/ˈækjərət/', 'CET4'),
('achieve', '实现；达到', '/əˈtʃiːv/', 'CET4'),
('acquire', '获得；取得', '/əˈkwaɪər/', 'CET4'),
('adapt', '适应；改编', '/əˈdæpt/', 'CET4'),
('adequate', '足够的；适当的', '/ˈædɪkwət/', 'CET4'),
('adjust', '调整；适应', '/əˈdʒʌst/', 'CET4'),
('administration', '管理；行政', '/ədˌmɪnɪˈstreɪʃn/', 'CET6'),
('admire', '钦佩；欣赏', '/ədˈmaɪər/', 'CET4'),
('admit', '承认；准许进入', '/ədˈmɪt/', 'CET4');
