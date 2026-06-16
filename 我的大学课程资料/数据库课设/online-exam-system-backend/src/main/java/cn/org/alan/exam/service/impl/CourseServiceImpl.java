package cn.org.alan.exam.service.impl;

import cn.org.alan.exam.mapper.CourseMapper;
import cn.org.alan.exam.model.entity.Course;
import cn.org.alan.exam.service.ICourseService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 * 课程服务实现类
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Service
public class CourseServiceImpl extends ServiceImpl<CourseMapper, Course> implements ICourseService {
}
