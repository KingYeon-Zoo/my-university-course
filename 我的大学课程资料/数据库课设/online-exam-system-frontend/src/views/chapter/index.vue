<template>
  <div class="app-container">
    <div class="filter-container" style="margin-bottom: 20px;">
      <span style="font-size: 14px; margin-right: 10px;">选择课程:</span>
      <el-select v-model="selectedCourseId" placeholder="请选择课程" clearable @change="handleCourseChange" style="margin-right: 15px; width: 220px;">
        <el-option
          v-for="item in courses"
          :key="item.id"
          :label="item.courseName"
          :value="item.id"
        />
      </el-select>
      <el-button type="primary" icon="el-icon-plus" :disabled="!selectedCourseId" @click="handleCreate">新增章节</el-button>
    </div>

    <!-- table -->
    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      :header-cell-style="{
        background: '#f2f3f4',
        color: '#555',
        'font-weight': 'bold',
        'line-height': '32px',
      }"
    >
      <el-table-column label="序号" align="center" width="80">
        <template slot-scope="scope">{{ scope.$index + 1 }}</template>
      </el-table-column>
      <el-table-column prop="chapterName" label="章节名称" align="center" />
      <el-table-column prop="sort" label="排序权重" align="center" width="100" />
      <el-table-column prop="createTime" label="创建时间" align="center">
        <template slot-scope="{row}">
          <span>{{ row.createTime | parseTime }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="220">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" icon="el-icon-edit" @click="handleUpdate(row)">编辑</el-button>
          <el-button type="danger" size="mini" icon="el-icon-delete" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- dialog -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogFormVisible" width="450px">
      <el-form ref="dataForm" :model="temp" :rules="rules" label-position="left" label-width="100px" style="width: 350px; margin-left:30px;">
        <el-form-item label="章节名称" prop="chapterName">
          <el-input v-model="temp.chapterName" placeholder="请输入章节名称" />
        </el-form-item>
        <el-form-item label="排序权重" prop="sort">
          <el-input-number v-model="temp.sort" :min="0" style="width: 150px;" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { listCourse } from '@/api/course'
import { listChapter, addChapter, updateChapter, deleteChapter } from '@/api/chapter'
import { parseTime } from '@/utils'

export default {
  name: 'ChapterManagement',
  filters: {
    parseTime(time) {
      if (!time) return ''
      const date = new Date(time)
      const format = '{y}-{m}-{d} {h}:{i}:{s}'
      return parseTime(date, format)
    }
  },
  data() {
    return {
      courses: [],
      selectedCourseId: undefined,
      list: [],
      listLoading: false,
      dialogStatus: '',
      dialogFormVisible: false,
      dialogTitle: '',
      temp: {
        id: undefined,
        courseId: undefined,
        chapterName: '',
        sort: 0
      },
      rules: {
        chapterName: [{ required: true, message: '章节名称为必填项', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getCourses()
  },
  methods: {
    getCourses() {
      listCourse().then(res => {
        if (res.code) {
          this.courses = res.data
          if (this.courses.length > 0) {
            this.selectedCourseId = this.courses[0].id
            this.getList()
          }
        }
      })
    },
    getList() {
      if (!this.selectedCourseId) {
        this.list = []
        return
      }
      this.listLoading = true
      listChapter(this.selectedCourseId).then(response => {
        if (response.code) {
          this.list = response.data
        } else {
          this.$message.error(response.msg || '获取章节列表失败')
        }
        this.listLoading = false
      }).catch(() => {
        this.listLoading = false
      })
    },
    handleCourseChange() {
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        courseId: this.selectedCourseId,
        chapterName: '',
        sort: 0
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogTitle = '新增章节'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          addChapter(this.temp).then(res => {
            if (res.code) {
              this.dialogFormVisible = false
              this.$message.success('创建章节成功')
              this.getList()
            } else {
              this.$message.error(res.msg || '创建章节失败')
            }
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      this.dialogStatus = 'update'
      this.dialogTitle = '编辑章节'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          updateChapter(tempData.id, tempData).then(res => {
            if (res.code) {
              this.dialogFormVisible = false
              this.$message.success('更新章节成功')
              this.getList()
            } else {
              this.$message.error(res.msg || '更新章节失败')
            }
          })
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确定要删除该章节吗？此操作不可逆。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteChapter(row.id).then(res => {
          if (res.code) {
            this.$message.success('删除章节成功')
            this.getList()
          } else {
            this.$message.error(res.msg || '删除章节失败')
          }
        })
      }).catch(() => {})
    }
  }
}
</script>
