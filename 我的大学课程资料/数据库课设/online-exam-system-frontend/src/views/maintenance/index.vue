<template>
  <div class="app-container">
    <el-tabs type="border-card">
      
      <!-- TAB 1: 备份与恢复 -->
      <el-tab-pane>
        <span slot="label"><i class="el-icon-receiving"></i> 数据库备份与恢复</span>
        <div style="margin-bottom: 20px;">
          <el-button type="primary" icon="el-icon-download" @click="handleBackup" :loading="backupLoading">一键备份数据库</el-button>
          <el-button type="success" icon="el-icon-refresh" @click="getBackups">刷新备份列表</el-button>
        </div>

        <el-table
          v-loading="tableLoading"
          :data="backupList"
          border
          style="width: 100%"
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
          <el-table-column prop="fileName" label="备份文件名" align="center" />
          <el-table-column prop="fileSize" label="文件大小 (Bytes)" align="center" width="150">
            <template slot-scope="{row}">
              <span>{{ row.fileSize | formatBytes }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="backupTime" label="备份时间" align="center" width="200">
            <template slot-scope="{row}">
              <span>{{ row.backupTime | parseTime }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="280">
            <template slot-scope="{row}">
              <el-button type="success" size="mini" icon="el-icon-refresh-left" @click="handleRestore(row)">恢复</el-button>
              <a :href="getDownloadUrl(row.fileName)" target="_blank" style="margin-left: 10px; margin-right: 10px;">
                <el-button type="primary" size="mini" icon="el-icon-download">下载</el-button>
              </a>
              <el-button type="danger" size="mini" icon="el-icon-delete" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- TAB 2: 存储过程 & 视图 -->
      <el-tab-pane>
        <span slot="label"><i class="el-icon-connection"></i> 存储过程与视图调用</span>
        
        <el-collapse v-model="activeCollapseNames">
          
          <!-- 存储过程 1 -->
          <el-collapse-item name="proc1">
            <template slot="title">
              <span style="font-size: 16px; font-weight: bold; color: #409EFF;"><i class="el-icon-magic-stick"></i> 存储过程 1：查询指定课程的题型与章节数量统计</span>
            </template>
            <div style="margin: 10px 0;">
              <span style="font-size: 14px; margin-right: 10px;">选择课程:</span>
              <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="callProc1" style="width: 220px;">
                <el-option
                  v-for="item in courses"
                  :key="item.id"
                  :label="item.courseName"
                  :value="item.id"
                />
              </el-select>
            </div>
            
            <el-row :gutter="20" style="margin-top: 15px;">
              <el-col :span="12">
                <el-card class="box-card">
                  <div slot="header" class="clearfix">
                    <span style="font-weight: bold;">题型统计结果集</span>
                  </div>
                  <el-table :data="proc1TypeData" border size="small">
                    <el-table-column prop="typeName" label="题型名称" align="center" />
                    <el-table-column prop="questionCount" label="题目数量" align="center" />
                  </el-table>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="box-card">
                  <div slot="header" class="clearfix">
                    <span style="font-weight: bold;">章节统计结果集</span>
                  </div>
                  <el-table :data="proc1ChapterData" border size="small">
                    <el-table-column prop="chapterName" label="章节名称" align="center" />
                    <el-table-column prop="questionCount" label="题目数量" align="center" />
                  </el-table>
                </el-card>
              </el-col>
            </el-row>
          </el-collapse-item>

          <!-- 存储过程 2 -->
          <el-collapse-item name="proc2">
            <template slot="title">
              <span style="font-size: 16px; font-weight: bold; color: #67C23A;"><i class="el-icon-pie-chart"></i> 存储过程 2：统计所有课程各题型的习题数量</span>
            </template>
            <div style="margin-bottom: 10px;">
              <el-button type="success" size="small" @click="callProc2">执行 proc_get_all_course_question_stats</el-button>
            </div>
            <el-table :data="proc2Data" border size="small">
              <el-table-column prop="course_name" label="课程名称" align="center" />
              <el-table-column prop="type_name" label="题型名称" align="center" />
              <el-table-column prop="question_count" label="习题数量" align="center" />
            </el-table>
          </el-collapse-item>

          <!-- 视图查询 -->
          <el-collapse-item name="view1">
            <template slot="title">
              <span style="font-size: 16px; font-weight: bold; color: #E6A23C;"><i class="el-icon-view"></i> 视图：查询各门课程使用的题型 (v_course_question_types)</span>
            </template>
            <div style="margin-bottom: 10px;">
              <el-button type="warning" size="small" @click="queryView">查询 v_course_question_types 视图数据</el-button>
            </div>
            <el-table :data="viewData" border size="small">
              <el-table-column prop="course_name" label="课程名称" align="center" />
              <el-table-column prop="type_name" label="可用题型" align="center" />
              <el-table-column prop="code" label="题型编码" align="center" />
            </el-table>
          </el-collapse-item>

        </el-collapse>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script>
import { triggerBackup, listBackup, triggerRestore, deleteBackup } from '@/api/backup'
import { listCourse } from '@/api/course'
import { getCourseStats, getAllCoursesStats, getCourseTypesFromView } from '@/api/dbObjects'
import { parseTime } from '@/utils'

export default {
  name: 'DatabaseMaintenance',
  filters: {
    parseTime(time) {
      if (!time) return ''
      return parseTime(new Date(time), '{y}-{m}-{d} {h}:{i}:{s}')
    },
    formatBytes(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
  },
  data() {
    return {
      // 备份列表
      backupList: [],
      tableLoading: false,
      backupLoading: false,
      
      // 存储过程与视图
      activeCollapseNames: ['proc1', 'proc2', 'view1'],
      courses: [],
      selectedCourseId: undefined,
      proc1TypeData: [],
      proc1ChapterData: [],
      proc2Data: [],
      viewData: []
    }
  },
  created() {
    this.getBackups()
    this.getCourses()
  },
  methods: {
    getBackups() {
      this.tableLoading = true
      listBackup().then(res => {
        if (res.code) {
          this.backupList = res.data
        }
        this.tableLoading = false
      }).catch(() => {
        this.tableLoading = false
      })
    },
    handleBackup() {
      this.backupLoading = true
      triggerBackup().then(res => {
        if (res.code) {
          this.$message.success(res.msg || '备份成功')
          this.getBackups()
        } else {
          this.$message.error(res.msg || '备份失败')
        }
        this.backupLoading = false
      }).catch(err => {
        this.$message.error('备份失败: ' + err.message)
        this.backupLoading = false
      })
    },
    handleRestore(row) {
      this.$confirm(`确定要将数据库还原到备份文件 [${row.fileName}] 的状态吗？此操作会导致当前数据被覆写！`, '警告', {
        confirmButtonText: '确定还原',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({
          lock: true,
          text: '正在还原数据库，这可能需要几十秒，请稍候...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        triggerRestore(row.fileName).then(res => {
          loading.close()
          if (res.code) {
            this.$message.success('数据库还原成功！')
          } else {
            this.$message.error(res.msg || '还原失败')
          }
        }).catch(err => {
          loading.close()
          this.$message.error('还原失败: ' + err.message)
        })
      }).catch(() => {})
    },
    handleDelete(row) {
      this.$confirm('确定要删除此备份文件吗？此操作不可撤销。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteBackup(row.fileName).then(res => {
          if (res.code) {
            this.$message.success('删除成功')
            this.getBackups()
          } else {
            this.$message.error(res.msg || '删除失败')
          }
        })
      }).catch(() => {})
    },
    getDownloadUrl(fileName) {
      // 拼接下载地址 (后端地址为 /api/backup/download/{fileName})
      const baseUrl = process.env.VUE_APP_BASE_API || ''
      return `${baseUrl}/backup/download/${fileName}`
    },
    
    // TAB 2 Methods
    getCourses() {
      listCourse().then(res => {
        if (res.code && res.data.length > 0) {
          this.courses = res.data
          this.selectedCourseId = this.courses[0].id
          this.callProc1()
        }
      })
    },
    callProc1() {
      if (!this.selectedCourseId) return
      getCourseStats(this.selectedCourseId).then(res => {
        if (res.code) {
          this.proc1TypeData = res.data.typeStats
          this.proc1ChapterData = res.data.chapterStats
        }
      })
    },
    callProc2() {
      getAllCoursesStats().then(res => {
        if (res.code) {
          this.proc2Data = res.data
          this.$message.success('存储过程 proc_get_all_course_question_stats 调用成功')
        }
      })
    },
    queryView() {
      getCourseTypesFromView().then(res => {
        if (res.code) {
          this.viewData = res.data
          this.$message.success('视图 v_course_question_types 查询成功')
        }
      })
    }
  }
}
</script>
