<template>
  <nav>
    <div class="logo"><!-- Add your logo here --></div>
    <ul>
      <li><a href="#">Home</a></li>
      <li><a href="#">About</a></li>
      <li><a href="#">Blog</a></li>
      <li><a href="#">Contact</a></li>
    </ul>
  </nav>

  <div class="admin-dashboard">
    <h1>Admin dashboard</h1>
    <div class="dashboard-grid">
      <div class="user-activity-chart">
        <h2>User Activity</h2>
        <!-- 这里使用实际的图表库，如 Chart.js 或 Echarts -->
        
      </div>
      
      <div class="model-management">
        <div class="tab-header">
          <button :class="{ active: activeTab === 'model' }" @click="activeTab = 'model'">MODEL MANAGEMENT</button>
          <button :class="{ active: activeTab === 'data' }" @click="activeTab = 'data'">DATA MANAGEMENT</button>
        </div>
        <div v-if="activeTab === 'model'" class="model-content">
          <h3>Add New Model</h3>
          <div class="model-form">
            <input v-model="newModelName" placeholder="Model Name" />
            <input type="file" @change="handleFileUpload" />
            <button @click="addModel">Add Model</button>
          </div>
          <h3>Existing Models</h3>
          <ul>
            <li>Random Forest Classifier (Active)</li>
            <li>Neural Network</li>
            <li>Support Vector Machine</li>
          </ul>
        </div>
        <div v-else class="data-content">
          <!-- Data management content -->
        </div>
      </div>
      
      <div class="detection-alert">
        <h2>Detection Alert</h2>
        <table>
          <thead>
            <tr>
              <th>USER</th>
              <th>MALWARE TYPE</th>
              <th>SEVERITY</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alert in detectionAlerts" :key="alert.user">
              <td>{{ alert.user }}</td>
              <td>{{ alert.malwareType }}</td>
              <td :class="alert.severity.toLowerCase()">{{ alert.severity }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="model-performance">
        <div class="tab-header">
          <button :class="{ active: performanceTab === 'performance' }" @click="performanceTab = 'performance'">MODEL PERFORMANCE</button>
          <button :class="{ active: performanceTab === 'insights' }" @click="performanceTab = 'insights'">DATA INSIGHTS</button>
        </div>
        <!-- 这里使用实际的图表库 -->
        <LineChart v-if="performanceTab === 'performance'" :chartData="modelPerformanceData" />
        <div v-else>
          <!-- Data insights content -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  components: {
  },
  setup() {
    const activeTab = ref('model');
    const performanceTab = ref('performance');
    const newModelName = ref('');
    const detectionAlerts = ref([
      { user: 'User1234', malwareType: 'Ransomware', severity: 'CRITICAL' },
      { user: 'User1235', malwareType: 'Trojan', severity: 'LOW' }
    ]);

    const userActivityData = ref({
      labels: ['27.08', '28.08', '29.08', '30.08', '31.08', '01.09', '02.09'],
      datasets: [
        {
          label: 'Total Scans',
          data: [500, 400, 350, 470, 550, 600, 580],
          borderColor: 'blue'
        },
        {
          label: 'Malware Detection',
          data: [20, 15, 10, 18, 22, 21, 20],
          borderColor: 'green'
        }
      ]
    });

    const modelPerformanceData = ref({
      labels: ['30.08', '31.08', '01.09', '02.09'],
      datasets: [
        {
          label: 'Model Performance',
          data: [0.95, 0.96, 0.97, 0.98],
          borderColor: 'purple'
        }
      ]
    });

    const handleFileUpload = (event) => {
      // 处理文件上传
    };

    const addModel = () => {
      // 添加新模型的逻辑
      console.log('Adding new model:', newModelName.value);
      newModelName.value = '';
    };

    onMounted(() => {
      // 可以在这里从API获取初始数据
    });

    return {
      activeTab,
      performanceTab,
      newModelName,
      detectionAlerts,
      userActivityData,
      modelPerformanceData,
      handleFileUpload,
      addModel
    };
  }
}
</script>

<style scoped>
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
}

nav ul {
  display: flex;
  list-style-type: none;
}

nav ul li {
  margin-right: 1rem;
}

.admin-dashboard {
  font-family: Arial, sans-serif;
  padding: 20px;
  background-color: #f0f0f0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.user-activity-chart, .model-management, .detection-alert, .model-performance {
  background-color: white;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.tab-header button {
  background: none;
  border: none;
  padding: 10px;
  cursor: pointer;
}

.tab-header button.active {
  border-bottom: 2px solid purple;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 8px;
  border-bottom: 1px solid #ddd;
}

.critical {
  color: red;
}

.low {
  color: green;
}

/* 添加更多样式以匹配设计 */
</style>