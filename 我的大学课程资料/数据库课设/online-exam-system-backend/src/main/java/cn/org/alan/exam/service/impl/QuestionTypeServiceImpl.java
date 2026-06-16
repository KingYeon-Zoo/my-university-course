package cn.org.alan.exam.service.impl;

import cn.org.alan.exam.mapper.QuestionTypeMapper;
import cn.org.alan.exam.model.entity.QuestionType;
import cn.org.alan.exam.service.IQuestionTypeService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 * 题型服务实现类
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Service
public class QuestionTypeServiceImpl extends ServiceImpl<QuestionTypeMapper, QuestionType> implements IQuestionTypeService {
}
