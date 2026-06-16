-- ========================================
-- 实验1：京东评论词频统计分析
-- 数据文件：/tmp/jd.csv
-- ========================================

-- 1.1 创建外部表读取京东评论数据
DROP TABLE IF EXISTS jd_comments_raw;
CREATE TABLE jd_comments_raw (
    comment_text STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\n'
STORED AS TEXTFILE;

-- 1.2 加载数据文件
LOAD DATA LOCAL INPATH '/tmp/jd.csv' INTO TABLE jd_comments_raw;

-- 1.3 创建词汇表用于存储分词结果
DROP TABLE IF EXISTS jd_words;
CREATE TABLE jd_words AS
SELECT 
    word,
    count(*) AS word_count
FROM (
    SELECT 
        trim(word_item) AS word
    FROM jd_comments_raw 
    LATERAL VIEW explode(split(regexp_replace(comment_text, '[^\\u4e00-\\u9fa5]', ' '), '\\s+')) word_table AS word_item
    WHERE length(trim(word_item)) >= 2 
      AND trim(word_item) != ''
) words_filtered
WHERE word != '' 
  AND word IS NOT NULL
GROUP BY word;

-- 1.4 查询实验1结果：京东评论词频统计（按词频降序排列）
SELECT 
    word       AS `词汇`,
    word_count AS `词频`
FROM jd_words
WHERE word_count > 1
ORDER BY word_count DESC, word ASC
LIMIT 50;


-- ========================================
-- 实验2：英文文本词频统计分析
-- 数据文件：/tmp/word_count_test.txt
-- ========================================

-- 2.1 创建外部表读取英文文本数据
DROP TABLE IF EXISTS english_text_raw;
CREATE TABLE english_text_raw (
    text_line STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\n'
STORED AS TEXTFILE;

-- 2.2 加载数据文件
LOAD DATA LOCAL INPATH '/tmp/word_count_test.txt' INTO TABLE english_text_raw;

-- 2.3 创建英文单词表用于存储分词结果
DROP TABLE IF EXISTS english_words;
CREATE TABLE english_words AS
SELECT 
    lower(word) AS word,
    count(*)   AS word_count
FROM (
    SELECT 
        regexp_replace(trim(word_item), '[^a-zA-Z]', '') AS word
    FROM english_text_raw 
    LATERAL VIEW explode(split(lower(text_line), '\\s+')) word_table AS word_item
    WHERE length(regexp_replace(trim(word_item), '[^a-zA-Z]', '')) >= 2
) words_filtered
WHERE word != '' 
  AND word IS NOT NULL
GROUP BY lower(word);

-- 2.4 查询实验2结果：英文词频统计（按词频降序排列）
SELECT 
    word AS `单词`,
    word_count AS `词频`
FROM english_words
ORDER BY word_count DESC, word ASC
LIMIT 30;


-- ========================================
-- 实验3：买家收藏商品数量统计分析
-- 数据文件：/tmp/experiment3_data.txt
-- ========================================

-- 3.1 创建表读取收藏数据
DROP TABLE IF EXISTS user_favorites_raw;
CREATE TABLE user_favorites_raw (
    line_data STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\n'
STORED AS TEXTFILE;

-- 3.2 加载数据文件
LOAD DATA LOCAL INPATH '/tmp/experiment3_data.txt' INTO TABLE user_favorites_raw;

-- 3.3 创建结构化的收藏数据表
DROP TABLE IF EXISTS user_favorites;
CREATE TABLE user_favorites AS
SELECT 
    cast(split(line_data, '\t')[0] AS int)   AS buyer_id,
    cast(split(line_data, '\t')[1] AS int)   AS product_id,
    split(line_data, '\t')[2]               AS favorite_date
FROM user_favorites_raw
WHERE line_data IS NOT NULL 
  AND line_data != ''
  AND size(split(line_data, '\t')) >= 3
  AND split(line_data, '\t')[0] RLIKE '^[0-9]+$'
  AND split(line_data, '\t')[1] RLIKE '^[0-9]+$';

-- 3.4 统计每个买家收藏商品数量
DROP TABLE IF EXISTS buyer_favorite_count;
CREATE TABLE buyer_favorite_count AS
SELECT 
    buyer_id,
    count(distinct product_id) AS favorite_count,
    count(*)               AS total_records,
    min(favorite_date)     AS earliest_date,
    max(favorite_date)     AS latest_date
FROM user_favorites
GROUP BY buyer_id;

-- 3.5 查询实验3结果：买家收藏统计（按收藏数量降序排列）
SELECT 
    buyer_id        AS `买家ID`,
    favorite_count  AS `收藏商品数量`,
    total_records   AS `收藏总次数`,
    earliest_date   AS `最早收藏时间`,
    latest_date     AS `最近收藏时间`
FROM buyer_favorite_count
ORDER BY favorite_count DESC, buyer_id ASC
LIMIT 20;


-- ========================================
-- 实验结果汇总
-- ========================================

-- 显示实验1统计摘要
SELECT 
    'JD Comments Analysis' AS experiment,
    count(*)            AS total_words,
    max(word_count)     AS max_frequency
FROM jd_words;

-- 显示实验2统计摘要
SELECT 
    'English Text Analysis' AS experiment,
    count(*)               AS total_words,
    max(word_count)        AS max_frequency
FROM english_words;

-- 显示实验3统计摘要
SELECT 
    'User Favorites Analysis'                  AS experiment,
    count(*)                                AS total_buyers,
    cast(avg(favorite_count) AS decimal(10,2)) AS avg_favorites_per_buyer,
    max(favorite_count)                     AS max_favorites
FROM buyer_favorite_count;

-- 查看各实验TOP结果
SELECT '=== 实验1词频TOP5 ===' AS title;
SELECT concat(word, ': ', cast(word_count AS string)) AS result
FROM jd_words
ORDER BY word_count DESC
LIMIT 5;

SELECT '=== 实验2词频TOP5 ===' AS title;
SELECT concat(word, ': ', cast(word_count AS string)) AS result
FROM english_words
ORDER BY word_count DESC
LIMIT 5;

SELECT '=== 实验3收藏TOP5 ===' AS title;
SELECT concat('Buyer ', cast(buyer_id AS string), ': ', cast(favorite_count AS string), ' items') AS result
FROM buyer_favorite_count
ORDER BY favorite_count DESC
LIMIT 5;
