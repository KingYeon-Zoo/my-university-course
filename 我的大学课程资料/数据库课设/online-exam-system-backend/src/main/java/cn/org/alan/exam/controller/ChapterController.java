package cn.org.alan.exam.controller;

import cn.org.alan.exam.common.result.Result;
import cn.org.alan.exam.model.entity.Chapter;
import cn.org.alan.exam.service.IChapterService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 章节管理控制器
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Api(tags = "章节管理相关接口")
@RestController
@RequestMapping("/api/chapter")
public class ChapterController {

    @Resource
    private IChapterService chapterService;

    @GetMapping("/list")
    @ApiOperation("获取章节列表（可按课程过滤）")
    @PreAuthorize("hasAnyAuthority('role_student','role_teacher','role_admin')")
    public Result<List<Chapter>> getChapterList(@RequestParam(value = "courseId", required = false) Integer courseId) {
        LambdaQueryWrapper<Chapter> queryWrapper = new LambdaQueryWrapper<Chapter>()
                .eq(Chapter::getIsDeleted, 0);
        if (courseId != null) {
            queryWrapper.eq(Chapter::getCourseId, courseId);
        }
        queryWrapper.orderByAsc(Chapter::getSort).orderByDesc(Chapter::getId);
        List<Chapter> list = chapterService.list(queryWrapper);
        return Result.success("获取章节列表成功", list);
    }

    @PostMapping
    @ApiOperation("添加章节")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<String> addChapter(@Validated @RequestBody Chapter chapter) {
        chapterService.save(chapter);
        return Result.success("添加章节成功");
    }

    @PutMapping("/{id}")
    @ApiOperation("修改章节")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<String> updateChapter(@Validated @RequestBody Chapter chapter, @PathVariable("id") Integer id) {
        chapter.setId(id);
        chapterService.updateById(chapter);
        return Result.success("修改章节成功");
    }

    @DeleteMapping("/{id}")
    @ApiOperation("删除章节")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<String> deleteChapter(@PathVariable("id") Integer id) {
        chapterService.removeById(id);
        return Result.success("删除章节成功");
    }
}
