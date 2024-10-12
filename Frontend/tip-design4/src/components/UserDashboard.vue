<template>
  <div class="dashboard space-background">
    <div class="dashboard-content">
      <div class="dashboard-grid">
        <div class="cybersecurity-tip">
          <h2>Cybersecurity Tip</h2>
          <p>{{ currentTip }}</p>
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
              accept=".csv"
            >
            <div v-if="!selectedFile">
              <div class="upload-icon">⇧</div>
              <p>Click to upload or drag and drop</p>
              <p>.CSV file only</p>
            </div>
            <div v-else>
              <p>Selected file: {{ selectedFile.name }}</p>
            </div>
          </div>
          <div class="upload-actions">
            <button @click="uploadFile" class="upload-btn" :disabled="!selectedFile || isUploading">
              Upload & Classify
            </button>
            <button @click="downloadTemplate" class="download-btn">
              Download template
            </button>
          </div>
        </div>
        
        <div class="processor-usage">
          <h2>Processor Usage Prediction</h2>
          <div class="date-inputs">
            <input type="date" v-model="startDate" placeholder="Start Date">
            <input type="date" v-model="endDate" placeholder="End Date">
            <button @click="predictProcessorUsage" class="predict-btn">Predict</button>
          </div>
          <div ref="processorUsageChart" style="width: 100%; height: 400px;"></div>
        </div>
        
        <div class="scan-log">
          <h2>Scan Log</h2>
          <table>
            <thead>
              <tr>
                <th>FILE NAME</th>
                <th>STATUS</th>
                <th>DATE</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="file in userFiles" :key="file._id" @click="handleFileClick(file._id)">
                <td>{{ file.filename }}</td>
                <td>{{ file.scan_status }}</td>
                <td>{{ formatDate(file.upload_time) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="malware-category">
          <h2>Malware Category Distribution</h2>
          <div ref="pieChart" style="width: 100%; height: 300px;"></div>
        </div>
        
        <div class="malware-family">
          <h2>Malware Family Distribution</h2>
          <div ref="malwareFamilyChart" style="width: 100%; height: 400px;"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick} from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  setup() {
    const currentTip = ref('Always keep your software and systems up to date.')
    const selectedFile = ref(null)
    const isDragging = ref(false)
    const isUploading = ref(false)
    const uploadStatus = ref('')
    const totalFiles = ref(0)
    const latestScan = ref(null)
    const userFiles = ref([])
    const currentFileId = ref(null)
    const scanResults = ref(null)
    const currentFileData = ref(null)
    const startDate = ref('')
    const endDate = ref('')
    const predictionData = ref(null)

    const fileInput = ref(null)
    const pieChart = ref(null)
    const processorUsageChart = ref(null)
    const malwareFamilyChart = ref(null)

    const malwareCategoryData = ref([])

    const pieChartInstance = ref(null)
    const malwareFamilyChartInstance = ref(null)
    const processorUsageChartInstance = ref(null)

    const triggerFileInput = () => {
      fileInput.value.click()
    }

    const onFileSelected = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        uploadStatus.value = ''
      }
    }

    const onDrop = (event) => {
      isDragging.value = false
      const file = event.dataTransfer.files[0]
      if (file) {
        selectedFile.value = file
        uploadStatus.value = ''
      }
    }

    const uploadFile = async () => {
      if (!selectedFile.value) return

      isUploading.value = true
      uploadStatus.value = 'Uploading...'

      const formData = new FormData()
      formData.append('file', selectedFile.value)

      try {
        const response = await axios.post('http://0.0.0.0:8080/file/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('userToken')}`
          }
        })

        uploadStatus.value = `File uploaded successfully. Scan status: ${response.data.scan_status}`
        if (response.data.file_id) {
          await fetchScanResult(response.data.file_id)
        }
      } catch (error) {
        console.error('Upload error:', error)
        uploadStatus.value = 'Error uploading file. Please try again.'
      } finally {
        isUploading.value = false
        selectedFile.value = null
      }

      await fetchUserFiles()
    }

    const downloadTemplate = () => {
      console.log('Downloading template')
      // Implement template download logic here
    }

    const fetchUserFiles = async () => {
      try {
        const response = await axios.get('http://0.0.0.0:8080/file/user-files/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('userToken')}`
          }
        });
        totalFiles.value = response.data.total_files;
        userFiles.value = response.data.files;
        
        if (userFiles.value.length > 0) {
          // 按上传时间排序文件，选择最新的文件
          const latestFile = userFiles.value.sort((a, b) => 
            new Date(b.upload_time) - new Date(a.upload_time)
          )[0];
          
          // 获取并显示最新文件的数据
          await fetchFileData(latestFile._id);
        }
      } catch (error) {
        console.error('Error fetching user files:', error);
      }
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString()
    }

    const fetchScanResult = async (fileId) => {
      try {
        const response = await axios.get(`http://0.0.0.0:8080/file/scan-result/${fileId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('userToken')}`
          }
        })
        scanResults.value = response.data.scan_results
        currentFileId.value = fileId
        createCharts()
      } catch (error) {
        console.error('Error fetching scan results:', error)
      }
    }

    const createCharts = () => {
      if (currentFileId.value && scanResults.value) {
        createPieChart()
        createMalwareFamilyChart()
      }
    }

    const createPieChart = () => {
      if (!pieChart.value) return;

      if (pieChartInstance.value) {
        pieChartInstance.value.dispose()
      }

      pieChartInstance.value = echarts.init(pieChart.value)

      const option = {
        title: {
          text: 'Malware Category Distribution',
          left: 'center',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          textStyle: {
            color: '#fff'
          }
        },
        series: [
          {
            name: 'Malware Category',
            type: 'pie',
            radius: '50%',
            data: malwareCategoryData.value,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              color: '#fff'
            }
          }
        ]
      };
      pieChartInstance.value.setOption(option)
    }

    const createMalwareFamilyChart = () => {
      if (!malwareFamilyChart.value) {
        console.warn('Malware family chart DOM element not found')
        return
      }

      // Dispose of the existing chart instance if it exists
      if (malwareFamilyChartInstance.value) {
        malwareFamilyChartInstance.value.dispose()
      }

      // Create new chart instance
      malwareFamilyChartInstance.value = echarts.init(malwareFamilyChart.value)

      const malwareFamilyData = currentFileData.value.scan_results.reduce((acc, result) => {
        const className = result['Predicted Class']
        const confidence = result['Confidence']
        if (acc[className]) {
          acc[className] += confidence
        } else {
          acc[className] = confidence
        }
        return acc
      }, {})

      const sortedData = Object.entries(malwareFamilyData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10) // Only show top 10

      if (sortedData.length === 0) {
        console.error('No valid data for Malware Family chart')
        return
      }

      const option = {
        title: {
          text: 'Top 10 Malware Family Distribution',
          left: 'center',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            return `${params[0].name}: ${params[0].value.toFixed(4)}`
          }
        },
        grid: {
          top: '10%',
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          axisLabel: {
            color: '#fff'
          }
        },
        yAxis: {
          type: 'category',
          data: sortedData.map(item => item[0]),
          axisLabel: {
            color: '#fff'
          }
        },
        series: [
          {
            name: 'Confidence',
            type: 'bar',
            data: sortedData.map(item => item[1]),
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#188df0' }
              ])
            }
          }
        ]
      }

      malwareFamilyChartInstance.value.setOption(option)
    }

    const fetchFileData = async (fileId) => {
      try {
        const response = await axios.get(`http://0.0.0.0:8080/file/scan-result/${fileId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('userToken')}`
          }
        })
        currentFileData.value = response.data
        updateMalwareCategoryData(response.data.scan_results)
        
        // Use nextTick to ensure DOM is updated before creating charts
        nextTick(() => {
          createPieChart()
          createMalwareFamilyChart()
        })
      } catch (error) {
        console.error('Error fetching file data:', error)
      }
    }

    const handleFileClick = (fileId) => {
      fetchFileData(fileId)
    }

    const predictProcessorUsage = async () => {
      if (!startDate.value || !endDate.value) {
        alert('Please select both start and end dates.')
        return
      }
      
      try {
        const response = await axios.post(`http://0.0.0.0:8080/file/predict/?start_date=${startDate.value}&end_date=${endDate.value}`, {
          start_date: startDate.value,
          end_date: endDate.value
        }, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('userToken')}`
          }
        })
        
        predictionData.value = response.data
        createProcessorUsageChart()
      } catch (error) {
        console.error('Error predicting processor usage:', error)
        alert('Error predicting processor usage. Please try again.')
      }
    }

    const createProcessorUsageChart = () => {
      if (!processorUsageChart.value) return

      if (processorUsageChartInstance.value) {
        processorUsageChartInstance.value.dispose()
      }

      processorUsageChartInstance.value = echarts.init(processorUsageChart.value)

      const option = {
        title: {
          text: 'Processor Usage Prediction',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        legend: {
          data: ['Actual', 'Predicted'],
          top: '30px'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: predictionData.value.timestamps
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: 'Actual',
            type: 'line',
            data: predictionData.value.actual,
            smooth: true,
            symbolSize: 5
          },
          {
            name: 'Predicted',
            type: 'line',
            data: predictionData.value.predicted,
            smooth: true,
            symbolSize: 5
          }
        ]
      }

      processorUsageChartInstance.value.setOption(option)
    }

    const updateMalwareCategoryData = (scanResults) => {
      if (!scanResults || !Array.isArray(scanResults)) return;

      // 创建一个对象来存储每个类别的总置信度
      const categoryConfidence = {};

      // 遍历扫描结果，累加每个类别的置信度
      scanResults.forEach(result => {
        const category = result['Predicted Class'];
        const confidence = result['Confidence'];
        if (categoryConfidence[category]) {
          categoryConfidence[category] += confidence;
        } else {
          categoryConfidence[category] = confidence;
        }
      });

      // 将累加的结果转换为 ECharts 所需的数据格式
      malwareCategoryData.value = Object.entries(categoryConfidence).map(([name, value]) => ({
        name,
        value
      }));
    }

    const handleResize = () => {
      pieChartInstance.value?.resize()
      malwareFamilyChartInstance.value?.resize()
      processorUsageChartInstance.value?.resize()
    }

    watch(() => currentFileData.value, (newValue) => {
      if (newValue && newValue.scan_results) {
        updateMalwareCategoryData(newValue.scan_results)
        createPieChart()
      }
    })

    onMounted(() => {
      fetchUserFiles()
      window.addEventListener('resize', handleResize)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
      pieChartInstance.value?.dispose()
      malwareFamilyChartInstance.value?.dispose()
      processorUsageChartInstance.value?.dispose()
    })

    return {
      currentTip,
      selectedFile,
      isDragging,
      isUploading,
      uploadStatus,
      totalFiles,
      latestScan,
      userFiles,
      currentFileId,
      scanResults,
      currentFileData,
      startDate,
      endDate,
      predictionData,
      fileInput,
      pieChart,
      processorUsageChart,
      malwareFamilyChart,
      triggerFileInput,
      onFileSelected,
      onDrop,
      uploadFile,
      downloadTemplate,
      formatDate,
      handleFileClick,
      predictProcessorUsage,
      pieChart,
      malwareFamilyChart,
      processorUsageChart
    }
  }
}
</script>

<style scoped>
.dashboard {
  font-family: Arial, sans-serif;
  min-height: 100vh;
  width: 100vw;
  padding: 20px;
  color: white;
}

.dashboard-content {
  position: relative;
  z-index: 1;
}

.space-background {
  background: linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
  position: relative;
  overflow: hidden;
}

.space-background::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
    radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
    radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px);
  background-size: 550px 550px, 350px 350px, 250px 250px;
  background-position: 0 0, 40px 60px, 130px 270px;
  animation: twinkle 10s linear infinite;
}

@keyframes twinkle {
  0% { transform: translateY(0); }
  100% { transform: translateY(-550px); }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.cybersecurity-tip, .upload-section, .processor-usage, .scan-log, .malware-category, .malware-family {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 20px;
}

h2 {
  margin-top: 0;
  margin-bottom: 15px;
}

.upload-area {
  border: 2px dashed #8e44ad;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
}

.upload-icon {
  font-size: 24px;
  margin-bottom: 10px;
}

.upload-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

.upload-btn, .download-btn, .predict-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.upload-btn {
  background-color: #8e44ad;
  color: white;
}

.download-btn {
  background-color: #27ae60;
  color: white;
}

.predict-btn {
  background-color: #8e44ad;
  color: white;
}

.date-inputs {
  display: flex;
  gap: 10px;
}

.date-inputs input {
  padding: 5px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

th {
  background-color: rgba(255, 255, 255, 0.05);
}

.scan-log table {
  cursor: pointer;
}

.scan-log tr:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.processor-usage img {
  margin-top: 20px;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

#processorUsageChart {
  width: 100%;
  height: 400px;
  margin-top: 20px;
}
</style>