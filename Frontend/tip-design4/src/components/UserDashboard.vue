<template>
  <div class="dashboard">
    <h1>User dashboard</h1>
    <div class="dashboard-content">
      <div class="stats-section">
        <div class="stat-card">
          <div>
            <span v-if="latestScan">{{ formatRelativeTime(latestScan.upload_time) }}</span>
            <h3>LATEST SCAN</h3>
          </div>
          <div>
            <h2>{{ totalFiles }}</h2>
            <h3>TOTAL SCANS</h3>
          </div>
        </div>
        <div class="stat-card">
          <div>
            <h2>18</h2>
            <h3>CLEAN FILES</h3>
          </div>
          <div>
            <h2>6</h2>
            <h3>DETECTED MALWARE</h3>
          </div>
        </div>
        <div class="pie-chart">
          <!-- 这里需要使用实际的图表库，如 Chart.js 或 Echarts -->
          <div>Pie Chart Placeholder</div>
        </div>
      </div>
      
      <div class="upload-section">
      <h2>UPLOAD A FILE</h2>
      <div
        class="upload-area"
        @dragover.prevent
        @dragleave.prevent
        @drop.prevent="onDrop"
        @click="triggerFileInput"
        :class="{ 'dragging': isDragging }"
      >
        <input
          type="file"
          ref="fileInput"
          @change="onFileSelected"
          style="display: none"
        >
        <div v-if="!selectedFile">
          <div class="upload-icon">File</div>
          <p>Drag and drop your file here or click to select</p>
        </div>
        <div v-else>
          <p>Selected file: {{ selectedFile.name }}</p>
          <p>File type: {{ selectedFile.type || 'Unknown' }}</p>
        </div>
      </div>
      <div class="download-template" @click="downloadTemplate">
        <span>DOWNLOAD template</span>
      </div>
      <button @click="uploadFile" class="scan-btn" :disabled="!selectedFile || isUploading">
        {{ isUploading ? 'UPLOADING...' : 'SCAN' }}
      </button>
      <p v-if="uploadStatus" :class="{ 'success': uploadStatus.includes('success'), 'error': uploadStatus.includes('error') }">
        {{ uploadStatus }}
      </p>
    </div>
      
    <div class="file-list">
        <h3>File Name</h3>
        <h3>Status</h3>
        <h3>Date</h3>
        <template v-if="userFiles.length">
          <template v-for="file in userFiles" :key="file._id">
            <div>{{ file.filename }}</div>
            <div>{{ file.scan_status }}</div>
            <div>{{ formatDate(file.upload_time) }}</div>
          </template>
        </template>
        <template v-else>
          <div colspan="3">No files uploaded yet.</div>
        </template>
      </div>
      
      <div class="charts-section">
        <div class="system-behavior-chart">
          <!-- 这里需要使用实际的图表库 -->
          <h3>System Behavior Over Time</h3>
          <div>Line Chart Placeholder</div>
        </div>
        <div class="malware-distribution">
          <h3>Malware Family Distribution</h3>
          <!-- 这里需要使用实际的图表库 -->
          <div>Bar Chart Placeholder</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Dashboard',
  data() {
    return {
      selectedFile: null,
      isDragging: false,
      isUploading: false,
      uploadStatus: '',
      totalFiles: 0,
      latestScan: null,
      userFiles: [],
      // 这里可以添加需要的数据
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    onFileSelected(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        this.uploadStatus = '';
      }
    },

    onDrop(event) {
      this.isDragging = false;
      const file = event.dataTransfer.files[0];
      if (file) {
        this.selectedFile = file;
        this.uploadStatus = '';
      }
    },

    async uploadFile() {
      if (!this.selectedFile) return;

      this.isUploading = true;
      this.uploadStatus = 'Uploading...';

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await axios.post('http://0.0.0.0:8080/file/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('userToken')}` // 假设你在登录时将 token 存储在 localStorage
          }
        });

        this.uploadStatus = `File uploaded successfully. Scan status: ${response.data.scan_status}`;
        // 可以在这里添加逻辑来更新文件列表或其他相关UI元素
      } catch (error) {
        console.error('Upload error:', error);
        this.uploadStatus = 'Error uploading file. Please try again.';
      } finally {
        this.isUploading = false;
        this.selectedFile = null; // 重置选中的文件
      }

      await this.fetchUserFiles();
    },

    downloadTemplate() {
      // 实现模板下载逻辑
      console.log('Downloading template');
      // 可以使用 window.open 或 axios 来下载模板文件
    },

    async fetchUserFiles() {
      try {
        const response = await axios.get('http://0.0.0.0:8080/file/user-files/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('userToken')}`
          }
        });
        this.totalFiles = response.data.total_files;
        this.userFiles = response.data.files;
        if (this.userFiles.length > 0) {
          this.latestScan = this.userFiles.reduce((latest, file) => 
            new Date(file.upload_time) > new Date(latest.upload_time) ? file : latest
          );
        }
      } catch (error) {
        console.error('Error fetching user files:', error);
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString(); // 使用浏览器的本地化设置格式化日期和时间
    },

    formatRelativeTime(dateString) {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffMinutes = Math.floor(diffTime / (1000 * 60));
      const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

      if (diffMinutes < 1) {
        return 'Just now';
      } else if (diffMinutes < 60) {
        return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
      } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      } else if (diffDays < 7) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
      } else {
        return this.formatDateTime(date);
      }
    },


    // 这里可以添加需要的方法
  },
  mounted() {
    this.fetchUserFiles();
    setInterval(() => {
      this.$forceUpdate();
    }, 60000);
    // 这里可以添加组件挂载后需要执行的逻辑，如获取数据等
  }
}
</script>

<style scoped>
.dashboard {
  background-color: #f5f0ff;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.stats-section {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.stat-card, .upload-section, .file-list, .charts-section {
  background-color: white;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.upload-section {
  text-align: center;
}

.upload-area {
  border: 2px dashed #8a2be2;
  border-radius: 10px;
  padding: 20px;
  margin: 10px 0;
}

.scan-btn {
  background-color: #8a2be2;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.file-list {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 10px;
}

.charts-section {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* 添加更多具体的样式以匹配图片中的设计 */
</style>