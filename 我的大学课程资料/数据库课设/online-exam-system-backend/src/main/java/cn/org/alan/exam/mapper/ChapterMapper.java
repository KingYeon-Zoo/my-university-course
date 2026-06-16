package cn.org.alan.exam.mapper;

import cn.org.alan.exam.model.entity.Chapter;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 章节 Mapper 接口
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Mapper
public interface ChapterMapper extends BaseMapper<Chapter> {
}
