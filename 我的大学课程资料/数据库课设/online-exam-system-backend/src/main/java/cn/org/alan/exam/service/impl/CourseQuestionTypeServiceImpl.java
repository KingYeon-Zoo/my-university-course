package cn.org.alan.exam.service.impl;

import cn.org.alan.exam.mapper.CourseQuestionTypeMapper;
import cn.org.alan.exam.model.entity.CourseQuestionType;
import cn.org.alan.exam.service.ICourseQuestionTypeService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 * 课程题型关联服务实现类
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Service
public class CourseQuestionTypeServiceImpl extends ServiceImpl<CourseQuestionTypeMapper, CourseQuestionType> implements ICourseQuestionTypeService {
}
