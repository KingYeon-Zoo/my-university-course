package cn.org.alan.exam.model.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.io.Serializable;
import java.util.Date;

/**
 * 章节实体类
 *
 * @author Antigravity
 * @since 2026-05-26
 */
@Data
@TableName("t_chapter")
@ApiModel(value = "章节实体", description = "课程章节信息")
public class Chapter implements Serializable {

    private static final long serialVersionUID = 1L;

    @ApiModelProperty(value = "章节ID")
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    @ApiModelProperty(value = "关联课程ID")
    @NotNull(message = "课程ID不能为空")
    private Integer courseId;

    @ApiModelProperty(value = "章节名称")
    @NotBlank(message = "章节名称不能为空")
    private String chapterName;

    @ApiModelProperty(value = "排序")
    private Integer sort = 0;

    @ApiModelProperty(value = "创建时间")
    private Date createTime;

    @ApiModelProperty(value = "是否删除")
    @TableLogic
    private Integer isDeleted = 0;
}
