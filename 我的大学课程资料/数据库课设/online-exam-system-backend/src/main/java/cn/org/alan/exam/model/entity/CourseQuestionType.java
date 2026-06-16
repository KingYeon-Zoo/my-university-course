package cn.org.alan.exam.model.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

import javax.validation.constraints.NotNull;
import java.io.Serializable;

/**
 * 课程题型关联实体类
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Data
@TableName("t_course_question_type")
@ApiModel(value = "课程题型关联实体", description = "课程所包含的题型")
public class CourseQuestionType implements Serializable {

    private static final long serialVersionUID = 1L;

    @ApiModelProperty(value = "关联ID")
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    @ApiModelProperty(value = "课程ID")
    @NotNull(message = "课程ID不能为空")
    private Integer courseId;

    @ApiModelProperty(value = "题型ID")
    @NotNull(message = "题型ID不能为空")
    private Integer questionTypeId;

    @ApiModelProperty(value = "是否删除")
    @TableLogic
    private Integer isDeleted = 0;
}
