-- 1. 创建课程表
CREATE TABLE IF NOT EXISTS `t_course` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '课程ID',
  `course_name` varchar(100) NOT NULL COMMENT '课程名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` int(11) NOT NULL DEFAULT '0' COMMENT '逻辑删除：0未删，1已删',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- 2. 创建章节表
CREATE TABLE IF NOT EXISTS `t_chapter` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '章节ID',
  `course_id` int(11) NOT NULL COMMENT '关联课程ID',
  `chapter_name` varchar(100) NOT NULL COMMENT '章节名称',
  `sort` int(11) DEFAULT '0' COMMENT '排序',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` int(11) NOT NULL DEFAULT '0' COMMENT '逻辑删除：0未删，1已删',
  PRIMARY KEY (`id`),
  KEY `idx_chapter_course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- 3. 创建题型表
CREATE TABLE IF NOT EXISTS `t_question_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '题型ID',
  `type_name` varchar(50) NOT NULL COMMENT '题型名称',
  `code` varchar(20) NOT NULL COMMENT '题型编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- 初始化基本题型数据
INSERT IGNORE INTO `t_question_type` (`id`, `type_name`, `code`) VALUES 
(1, '单选题', 'radio'),
(2, '多选题', 'multi'),
(3, '判断题', 'judge'),
(4, '简答题', 'saq');

-- 4. 创建课程题型关联表
CREATE TABLE IF NOT EXISTS `t_course_question_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `course_id` int(11) NOT NULL COMMENT '课程ID',
  `question_type_id` int(11) NOT NULL COMMENT '题型ID',
  `is_deleted` int(11) NOT NULL DEFAULT '0' COMMENT '逻辑删除',
  PRIMARY KEY (`id`),
  KEY `idx_cqt_course` (`course_id`),
  KEY `idx_cqt_qtype` (`question_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- 5. 修改习题表添加课程、章节、题型、抽取次数属性，并更新创建时间为默认当前时间
ALTER TABLE `t_question` ADD COLUMN `course_id` int(11) DEFAULT NULL COMMENT '课程ID';
ALTER TABLE `t_question` ADD COLUMN `chapter_id` int(11) DEFAULT NULL COMMENT '章节ID';
ALTER TABLE `t_question` ADD COLUMN `question_type_id` int(11) DEFAULT NULL COMMENT '题型ID';
ALTER TABLE `t_question` ADD COLUMN `extract_count` int(11) DEFAULT '0' COMMENT '抽取次数';
ALTER TABLE `t_question` MODIFY COLUMN `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';

-- 6. 创建视图：查询各门课程使用的题型
CREATE OR REPLACE VIEW `v_course_question_types` AS
SELECT 
  c.id AS course_id,
  c.course_name,
  qt.id AS question_type_id,
  qt.type_name,
  qt.code
FROM t_course_question_type cqt
JOIN t_course c ON cqt.course_id = c.id
JOIN t_question_type qt ON cqt.question_type_id = qt.id
WHERE cqt.is_deleted = 0 AND c.is_deleted = 0;

-- 7. 创建触发器：当习题被抽取加入试卷明细时，自动将该习题的抽取次数加 1
DROP TRIGGER IF EXISTS `tri_increment_extract_count`;
DELIMITER //
CREATE TRIGGER `tri_increment_extract_count` AFTER INSERT ON `t_exam_question`
FOR EACH ROW
BEGIN
  UPDATE `t_question` 
  SET `extract_count` = `extract_count` + 1 
  WHERE `id` = NEW.question_id;
END;
//
DELIMITER ;

-- 8. 存储过程 1：查询指定课程中各种题型和各章节的习题数量
DROP PROCEDURE IF EXISTS `proc_get_course_question_stats`;
DELIMITER //
CREATE PROCEDURE `proc_get_course_question_stats`(IN p_course_id INT)
BEGIN
  -- 1. 按题型统计数量
  SELECT qt.type_name, COUNT(q.id) AS question_count
  FROM t_question_type qt
  LEFT JOIN t_question q ON q.question_type_id = qt.id AND q.course_id = p_course_id AND q.is_deleted = 0
  GROUP BY qt.id;

  -- 2. 按章节统计数量
  SELECT c.chapter_name, COUNT(q.id) AS question_count
  FROM t_chapter c
  LEFT JOIN t_question q ON q.chapter_id = c.id AND q.is_deleted = 0
  WHERE c.course_id = p_course_id AND c.is_deleted = 0
  GROUP BY c.id;
END;
//
DELIMITER ;

-- 9. 存储过程 2：实现查询各门课程、各种题型的习题数量
DROP PROCEDURE IF EXISTS `proc_get_all_course_question_stats`;
DELIMITER //
CREATE PROCEDURE `proc_get_all_course_question_stats`()
BEGIN
  SELECT co.course_name, qt.type_name, COUNT(q.id) AS question_count
  FROM t_course co
  CROSS JOIN t_question_type qt
  LEFT JOIN t_question q ON q.course_id = co.id AND q.question_type_id = qt.id AND q.is_deleted = 0
  WHERE co.is_deleted = 0
  GROUP BY co.id, qt.id;
END;
//
DELIMITER ;

-- 10. 存储过程 3：自动抽题组成套题
DROP PROCEDURE IF EXISTS `proc_auto_assemble_paper`;
DELIMITER //
CREATE PROCEDURE `proc_auto_assemble_paper`(
  IN p_course_id INT,
  IN p_title VARCHAR(255),
  IN p_exam_duration INT,
  IN p_passed_score INT,
  IN p_radio_count INT,
  IN p_radio_score INT,
  IN p_multi_count INT,
  IN p_multi_score INT,
  IN p_judge_count INT,
  IN p_judge_score INT,
  IN p_saq_count INT,
  IN p_saq_score INT,
  IN p_user_id INT,
  OUT p_new_exam_id INT
)
BEGIN
  DECLARE v_gross_score INT DEFAULT 0;
  
  -- 计算总分数
  SET v_gross_score = (p_radio_count * p_radio_score) + (p_multi_count * p_multi_score) + (p_judge_count * p_judge_score) + (p_saq_count * p_saq_score);
  
  -- 插入试卷表
  INSERT INTO t_exam (
    title, exam_duration, passed_score, gross_score, max_count, user_id, 
    radio_count, radio_score, multi_count, multi_score, 
    judge_count, judge_score, saq_count, saq_score, 
    start_time, end_time, create_time, is_deleted
  )
  VALUES (
    p_title, p_exam_duration, p_passed_score, v_gross_score, 1, p_user_id, 
    p_radio_count, p_radio_score * 100, p_multi_count, p_multi_score * 100, 
    p_judge_count, p_judge_score * 100, p_saq_count, p_saq_score * 100, 
    NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), NOW(), 0
  );
  
  -- 获取新插入的试卷ID
  SET p_new_exam_id = LAST_INSERT_ID();
  
  -- 1. 抽取单选题并插入明细 (题型ID = 1, type = 1)
  IF p_radio_count > 0 THEN
    INSERT INTO t_exam_question (exam_id, question_id, score, sort, type)
    SELECT p_new_exam_id, q.id, p_radio_score, 0, 1
    FROM t_question q
    WHERE q.course_id = p_course_id AND q.question_type_id = 1 AND q.is_deleted = 0
    ORDER BY RAND()
    LIMIT p_radio_count;
  END IF;
  
  -- 2. 抽取多选题并插入明细 (题型ID = 2, type = 2)
  IF p_multi_count > 0 THEN
    INSERT INTO t_exam_question (exam_id, question_id, score, sort, type)
    SELECT p_new_exam_id, q.id, p_multi_score, 0, 2
    FROM t_question q
    WHERE q.course_id = p_course_id AND q.question_type_id = 2 AND q.is_deleted = 0
    ORDER BY RAND()
    LIMIT p_multi_count;
  END IF;
  
  -- 3. 抽取判断题并插入明细 (题型ID = 3, type = 3)
  IF p_judge_count > 0 THEN
    INSERT INTO t_exam_question (exam_id, question_id, score, sort, type)
    SELECT p_new_exam_id, q.id, p_judge_score, 0, 3
    FROM t_question q
    WHERE q.course_id = p_course_id AND q.question_type_id = 3 AND q.is_deleted = 0
    ORDER BY RAND()
    LIMIT p_judge_count;
  END IF;
  
  -- 4. 抽取简答题并插入明细 (题型ID = 4, type = 4)
  IF p_saq_count > 0 THEN
    INSERT INTO t_exam_question (exam_id, question_id, score, sort, type)
    SELECT p_new_exam_id, q.id, p_saq_score, 0, 4
    FROM t_question q
    WHERE q.course_id = p_course_id AND q.question_type_id = 4 AND q.is_deleted = 0
    ORDER BY RAND()
    LIMIT p_saq_count;
  END IF;
END;
//
DELIMITER ;
