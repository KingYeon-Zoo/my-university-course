package cn.org.alan.exam.controller;

import cn.org.alan.exam.common.result.Result;
import cn.org.alan.exam.model.entity.Course;
import cn.org.alan.exam.service.ICourseService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 课程管理控制器
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Api(tags = "课程管理相关接口")
@RestController
@RequestMapping("/api/course")
public class CourseController {

    @Resource
    private ICourseService courseService;

    @GetMapping("/list")
    @ApiOperation("获取所有课程列表")
    @PreAuthorize("hasAnyAuthority('role_student','role_teacher','role_admin')")
    public Result<List<Course>> getCourseList() {
        List<Course> list = courseService.list(new LambdaQueryWrapper<Course>()
                .eq(Course::getIsDeleted, 0)
                .orderByDesc(Course::getId));
        return Result.success("获取课程列表成功", list);
    }

    @PostMapping
    @ApiOperation("添加课程")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<String> addCourse(@Validated @RequestBody Course course) {
        courseService.save(course);
        return Result.success("添加课程成功");
    }

    @PutMapping("/{id}")
    @ApiOperation("修改课程")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<String> updateCourse(@Validated @RequestBody Course course, @PathVariable("id") Integer id) {
        course.setId(id);
        courseService.updateById(course);
        return Result.success("修改课程成功");
    }

    @DeleteMapping("/{id}")
    @ApiOperation("删除课程")
    @PreAuthorize("hasAnyAuthority('role_teacher','role_admin')")
    public Result<String> deleteCourse(@PathVariable("id") Integer id) {
        courseService.removeById(id);
        return Result.success("删除课程成功");
    }
}
