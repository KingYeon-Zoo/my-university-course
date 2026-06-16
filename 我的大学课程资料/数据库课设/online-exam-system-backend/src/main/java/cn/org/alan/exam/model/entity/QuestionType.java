package cn.org.alan.exam.model.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.io.Serializable;

/**
 * 题型实体类
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Data
@TableName("t_question_type")
@ApiModel(value = "题型实体", description = "系统题型定义")
public class QuestionType implements Serializable {

    private static final long serialVersionUID = 1L;

    @ApiModelProperty(value = "题型ID")
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    @ApiModelProperty(value = "题型名称")
    @NotBlank(message = "题型名称不能为空")
    private String typeName;

    @ApiModelProperty(value = "题型编码")
    @NotBlank(message = "题型编码不能为空")
    private String code;
}
