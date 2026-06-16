<template>
  <div class="app-container">
    <el-form
      ref="postForm"
      :model="postForm"
      :rules="rules"
      label-position="left"
      label-width="150px"
    >
      <el-card>
        <el-form-item label="归属课程" prop="courseId">
          <el-select
            v-model="postForm.courseId"
            placeholder="请选择课程"
            clearable
            @change="handleCourseChange"
            style="width: 400px"
          >
            <el-option
              v-for="item in coursesList"
              :key="item.id"
              :label="item.courseName"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="归属章节" prop="chapterId">
          <el-select
            v-model="postForm.chapterId"
            placeholder="请先选择课程"
            clearable
            :disabled="!postForm.courseId"
            style="width: 400px"
          >
            <el-option
              v-for="item in chaptersList"
              :key="item.id"
              :label="item.chapterName"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="题型选择" prop="questionTypeId">
          <el-select
            v-model="postForm.questionTypeId"
            placeholder="请先选择课程"
            clearable
            :disabled="!postForm.courseId"
            @change="handleQuestionTypeChange"
            style="width: 400px"
          >
            <el-option
              v-for="item in questionTypesList"
              :key="item.id"
              :label="item.typeName"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="归属题库" prop="repoId">
          <repo-select v-model="postForm.repoId" :multi="false" style="width: 400px" />
        </el-form-item>

        <el-form-item label="题目内容" prop="content">
          <el-input
            v-model="postForm.content"
            type="textarea"
            :rows="4"
            resize="vertical"
            style="width: 1200px"
          />
        </el-form-item>

        <el-form-item label="试题图片" style="margin-left: 7px">
          <file-upload v-model="postForm.image" accept=".jpg,.jepg,.png" />
        </el-form-item>

        <el-form-item label="整题解析" prop="oriPrice" style="margin-left: 7px">
          <el-input
            v-model="postForm.analysis"
            :precision="1"
            :max="999999"
            type="textarea"
            :rows="12"
            resize="vertical"
            style="width: 1200px"
          />
        </el-form-item>
      </el-card>

      <div
        v-if="postForm.quType  != 4"
        class="filter-container"
        style="margin-top: 25px"
      >
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-plus"
          size="small"
          plain
          @click="handleAdd"
        >
          添加
        </el-button>

        <el-table :data="postForm.options.filter(option => !option.isDeleted)" :border="true" style="width: 90%">
          <el-table-column label="是否答案" width="120" align="center">
            <template v-slot="scope">
              <el-checkbox v-model="scope.row.isRight">答案</el-checkbox>
            </template>
          </el-table-column>

          <el-table-column
            v-if="itemImage"
            label="选项图片"
            width="120px"
            align="center"
          >
            <template v-slot="scope">
              <file-upload v-model="scope.row.image" accept=".jpg,.jepg,.png" />
            </template>
          </el-table-column>

          <el-table-column label="答案内容">
            <template v-slot="scope">
              <el-input v-model="scope.row.content" type="textarea" />
            </template>
          </el-table-column>

          <!-- <el-table-column
            label="答案解析"
          >
            <template v-slot="scope">
              <el-input v-model="scope.row.analysis" type="textarea" />
            </template>
          </el-table-column> -->

          <el-table-column label="操作" align="center" width="100px">
            <template v-slot="scope">
              <el-button
                type="danger"
                icon="el-icon-delete"
                circle
                @click="removeItem(scope.$index)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-table
        v-if="postForm.quType == 4"
        :data="postForm.options"
        :border="true"
        style="width: 90%; margin-top: 30px"
      >
        <el-table-column label="答案内容">
          <template v-slot="scope">
            <el-input v-model="scope.row.content" type="textarea" />
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px">
        <el-button type="primary" @click="submitForm">保存</el-button>
        <el-button type="info" @click="onCancel">返回</el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { fetchDetail, quAdd, quDetail, quUpdate } from '@/api/question'
import { listCourse } from '@/api/course'
import { listChapter } from '@/api/chapter'
import { getTypesByCourse } from '@/api/questionType'
import RepoSelect from '@/components/RepoSelect'
import FileUpload from '@/components/FileUpload'

export default {

  name: 'QuDetail',
  components: { FileUpload, RepoSelect },

  data() {
    return {
      quId: '',
      quTypeDisabled: false,
      itemImage: true,

      coursesList: [],
      chaptersList: [],
      questionTypesList: [],

      levels: [
        { value: 1, label: '普通' },
        { value: 2, label: '较难' }
      ],

      postForm: {
        repoId: '',
        courseId: '',
        chapterId: '',
        questionTypeId: '',
        quType: '',
        options: []
      },
      rules: {
        content: [{ required: true, message: '题目内容不能为空！' }],
        courseId: [{ required: true, message: '必须选择归属课程！', trigger: 'change' }],
        chapterId: [{ required: true, message: '必须选择归属章节！', trigger: 'change' }],
        questionTypeId: [{ required: true, message: '必须选择题型！', trigger: 'change' }],
        repoId: [{ required: true, message: '请先选择题库！' }]
      }
    }
  },
  created() {
    this.getCourses()
    
    // 添加试题初始化
    const id = this.$route.params.id
    if (typeof id  != 'undefined') {
      this.quTypeDisabled = true
      this.fetchData(id)
    }
    // 编辑试题初始化
    this.quId = localStorage.getItem('quId')
    if (this.quId) {
      this.getQuDetail()
    }
  },
  beforeDestroy() {
    localStorage.removeItem('quId')
    this.postForm = {}
  },
  methods: {
    getCourses() {
      listCourse().then(res => {
        if (res.code) {
          this.coursesList = res.data
        }
      })
    },
    handleCourseChange(courseId) {
      this.postForm.chapterId = ''
      this.postForm.questionTypeId = ''
      this.chaptersList = []
      this.questionTypesList = []
      if (courseId) {
        listChapter(courseId).then(res => {
          if (res.code) {
            this.chaptersList = res.data
          }
        })
        getTypesByCourse(courseId).then(res => {
          if (res.code) {
            this.questionTypesList = res.data
          }
        })
      }
    },
    handleQuestionTypeChange(typeId) {
      // 通过题型ID(1-单选,2-多选,3-判断,4-简答)同步设置 quType 并重新初始化选项
      if (typeId) {
        this.postForm.quType = typeId
        this.handleTypeChange(typeId)
      }
    },
    // 获取单题详情
    async getQuDetail() {
      const res = await quDetail(this.quId)
      if (res.code) {
        res.data.options.forEach(item => {
          if (item.isRight) {
            item.isRight = true
          } else {
            item.isRight = false
          }
        })
        this.postForm = res.data
        // 如果有courseId，加载对应的 chapters 和 types
        if (this.postForm.courseId) {
          listChapter(this.postForm.courseId).then(r => {
            if (r.code) this.chaptersList = r.data
          })
          getTypesByCourse(this.postForm.courseId).then(r => {
            if (r.code) this.questionTypesList = r.data
          })
        }
      }
    },
    handleTypeChange(v) {
      this.postForm.options = []
      if (v === 3) {
        this.postForm.options.push({ isRight: true, content: '正确' })
        this.postForm.options.push({ isRight: false, content: '错误' })
      }

      if (v === 1 || v === 2) {
        this.postForm.options.push({ isRight: false, content: '' })
        this.postForm.options.push({ isRight: false, content: '' })
        this.postForm.options.push({ isRight: false, content: '' })
        this.postForm.options.push({ isRight: false, content: '' })
      }
      if (v === 4) {
        this.postForm.options.push({ isRight: true, content: '' })
      }
    },

    // 添加子项
    handleAdd() {
      this.postForm.options.push({ isRight: false, content: '' })
    },

    removeItem(index) {
      const actualIndex = this.postForm.options.findIndex((option, idx) => {
        return idx === index && !option.isDeleted
      })
      if (actualIndex !== -1) {
        // 将选项标记为已删除
        this.postForm.options[actualIndex].isDeleted = 1
        // 更新选项的排序
        this.postForm.options.forEach((option, idx) => {
          if (!option.isDeleted) {
            option.sort = idx
          }
        })
      }
    },

    fetchData(id) {
      fetchDetail(id).then((response) => {
        this.postForm = response.data
      })
    },
    submitForm() {
      (JSON.stringify(this.postForm))

      let rightCount = 0

      this.postForm.options.forEach(function(item) {
        if (item.isRight) {
          rightCount += 1
        }
      })

      if (this.postForm.quType === 1) {
        if (rightCount  != 1) {
          this.$message({
            message: '单选题答案只能有一个',
            type: 'warning'
          })

          return
        }
      }

      if (this.postForm.quType === 2) {
        if (rightCount < 2) {
          this.$message({
            message: '多选题至少要有两个正确答案！',
            type: 'warning'
          })

          return
        }
      }

      if (this.postForm.quType === 3) {
        if (rightCount  != 1) {
          this.$message({
            message: '判断题只能有一个正确项！',
            type: 'warning'
          })

          return
        }
      }

      this.$refs.postForm.validate((valid) => {
        if (!valid) {
          return
        }
        // 选项是否正确转型
        for (let i = 0; i < this.postForm.options.length; i++) {
          const option = this.postForm.options[i]
          if (option.isRight) {
            option.isRight = 1
          } else {
            option.isRight = 0
          }
        }

        if (this.quId) {
          // 修改试题
          quUpdate(this.quId, this.postForm).then(res => {
            if (res.code) {
              this.$notify({
                title: '成功',
                message: `${res.msg}`,
                type: 'success',
                duration: 2000
              })
              this.$router.push({ name: 'questions-management' })
            } else {
              this.$notify({
                title: '失败',
                message: `${res.msg}`,
                type: 'error',
                duration: 2000
              })
            }
          })
        } else {
          // 添加试题
          quAdd(this.postForm).then((response) => {
            this.postForm = response.data
            if (response.code) {
              this.$notify({
                title: '成功',
                message: '试题保存成功！',
                type: 'success',
                duration: 2000
              })

              this.$router.push({ name: 'questions-management' })
            } else {
              this.$notify({
                title: '失败',
                message: `${response.msg}`,
                type: 'error',
                duration: 2000
              })
            }
          })
        }
      })
    },
    onCancel() {
      this.$router.push({ name: 'questions-management' })
    }
  }
}
</script>

<style scoped>
.el-button--primary.is-plain {
  color: #409eff;
  background: #ecf5ff;
  border-color: #b3d8ff;
  margin-bottom: 25px;
}

.el-form-item {
  margin-bottom: 22px;
}

.el-textarea__inner {
  min-height: 120px;
  font-size: 14px;
  line-height: 1.5;
}

.el-form-item__label {
  font-weight: 500;
}
</style>
