package cn.org.alan.exam.mapper;

import cn.org.alan.exam.model.entity.CourseQuestionType;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 课程题型关联 Mapper 接口
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Mapper
public interface CourseQuestionTypeMapper extends BaseMapper<CourseQuestionType> {
}
