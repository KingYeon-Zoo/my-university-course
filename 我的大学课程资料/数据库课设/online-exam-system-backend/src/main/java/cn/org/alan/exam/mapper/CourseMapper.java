package cn.org.alan.exam.mapper;

import cn.org.alan.exam.model.entity.Course;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * 课程 Mapper 接口
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Mapper
public interface CourseMapper extends BaseMapper<Course> {
}
