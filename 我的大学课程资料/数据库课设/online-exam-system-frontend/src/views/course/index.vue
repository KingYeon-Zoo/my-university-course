<template>
  <div class="app-container">
    <div class="filter-container" style="margin-bottom: 20px;">
      <el-button type="primary" icon="el-icon-plus" @click="handleCreate">新增课程</el-button>
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
      <el-table-column prop="courseName" label="课程名称" align="center" />
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
        <el-form-item label="课程名称" prop="courseName">
          <el-input v-model="temp.courseName" placeholder="请输入课程名称" />
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
import { listCourse, addCourse, updateCourse, deleteCourse } from '@/api/course'
import { parseTime } from '@/utils'

export default {
  name: 'CourseManagement',
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
      list: [],
      listLoading: true,
      dialogStatus: '',
      dialogFormVisible: false,
      dialogTitle: '',
      temp: {
        id: undefined,
        courseName: ''
      },
      rules: {
        courseName: [{ required: true, message: '课程名称为必填项', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      listCourse().then(response => {
        if (response.code) {
          this.list = response.data
        } else {
          this.$message.error(response.msg || '获取课程列表失败')
        }
        this.listLoading = false
      }).catch(() => {
        this.listLoading = false
      })
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        courseName: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogTitle = '新增课程'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          addCourse(this.temp).then(res => {
            if (res.code) {
              this.dialogFormVisible = false
              this.$message.success('创建课程成功')
              this.getList()
            } else {
              this.$message.error(res.msg || '创建课程失败')
            }
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.dialogStatus = 'update'
      this.dialogTitle = '编辑课程'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          updateCourse(tempData.id, tempData).then(res => {
            if (res.code) {
              this.dialogFormVisible = false
              this.$message.success('更新课程成功')
              this.getList()
            } else {
              this.$message.error(res.msg || '更新课程失败')
            }
          })
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确定要删除该课程吗？这可能会影响关联的章节和题目。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteCourse(row.id).then(res => {
          if (res.code) {
            this.$message.success('删除课程成功')
            this.getList()
          } else {
            this.$message.error(res.msg || '删除课程失败')
          }
        })
      }).catch(() => {})
    }
  }
}
</script>
