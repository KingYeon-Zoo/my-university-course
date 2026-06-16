package cn.org.alan.exam.controller;

import cn.org.alan.exam.common.result.Result;
import cn.org.alan.exam.model.entity.CourseQuestionType;
import cn.org.alan.exam.model.entity.QuestionType;
import cn.org.alan.exam.service.ICourseQuestionTypeService;
import cn.org.alan.exam.service.IQuestionTypeService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 题型管理控制器
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Api(tags = "题型管理相关接口")
@RestController
@RequestMapping("/api/question-type")
public class QuestionTypeController {

    @Resource
    private IQuestionTypeService questionTypeService;

    @Resource
    private ICourseQuestionTypeService courseQuestionTypeService;

    @GetMapping("/list")
    @ApiOperation("获取系统所有题型列表")
    @PreAuthorize("hasAnyAuthority('role_student','role_teacher','role_admin')")
    public Result<List<QuestionType>> getQuestionTypeList() {
        List<QuestionType> list = questionTypeService.list();
        return Result.success("获取所有题型成功", list);
    }

    @GetMapping("/course/{courseId}")
    @ApiOperation("获取指定课程启用的题型列表")
    @PreAuthorize("hasAnyAuthority('role_student','role_teacher','role_admin')")
    public Result<List<QuestionType>> getTypesByCourse(@PathVariable("courseId") Integer courseId) {
        // 先查出课程关联的题型ID
        List<CourseQuestionType> links = courseQuestionTypeService.list(
                new LambdaQueryWrapper<CourseQuestionType>()
                        .eq(CourseQuestionType::getCourseId, courseId)
                        .eq(CourseQuestionType::getIsDeleted, 0));
        
        if (links.isEmpty()) {
            return Result.success("该课程暂无启用题型");
        }

        List<Integer> typeIds = links.stream().map(CourseQuestionType::getQuestionTypeId).collect(Collectors.toList());
        List<QuestionType> list = questionTypeService.list(new LambdaQueryWrapper<QuestionType>().in(QuestionType::getId, typeIds));
        return Result.success("获取课程题型成功", list);
    }

    @PostMapping("/course/{courseId}")
    @ApiOperation("配置/更新课程对应的题型")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<String> updateCourseTypes(@PathVariable("courseId") Integer courseId, @RequestBody List<Integer> typeIds) {
        // 先逻辑删除该课程已有的所有关联关系
        CourseQuestionType temp = new CourseQuestionType();
        temp.setIsDeleted(1);
        courseQuestionTypeService.update(temp, new LambdaQueryWrapper<CourseQuestionType>()
                .eq(CourseQuestionType::getCourseId, courseId));

        if (typeIds != null && !typeIds.isEmpty()) {
            List<CourseQuestionType> newLinks = typeIds.stream().map(typeId -> {
                CourseQuestionType link = new CourseQuestionType();
                link.setCourseId(courseId);
                link.setQuestionTypeId(typeId);
                link.setIsDeleted(0);
                return link;
            }).collect(Collectors.toList());
            courseQuestionTypeService.saveBatch(newLinks);
        }

        return Result.success("配置课程题型成功");
    }
}
