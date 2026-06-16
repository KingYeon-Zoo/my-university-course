package cn.org.alan.exam.service.impl;

import cn.org.alan.exam.mapper.ChapterMapper;
import cn.org.alan.exam.model.entity.Chapter;
import cn.org.alan.exam.service.IChapterService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 * 章节服务实现类
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Service
public class ChapterServiceImpl extends ServiceImpl<ChapterMapper, Chapter> implements IChapterService {
}
