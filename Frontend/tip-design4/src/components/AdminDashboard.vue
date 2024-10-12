<template>
  <div class="admin-dashboard space-background">
    <nav class="top-nav">
      <div class="logo"><!-- Add your logo here --></div>
      <ul class="nav-links">
        <li><a href="#">Home</a></li>
        <li><a href="#">About</a></li>
        <li><a href="#">Blog</a></li>
        <li><a href="#">Contact</a></li>
      </ul>
    </nav>

    <div class="dashboard-content">
      <h1>Admin dashboard</h1>
      <div class="dashboard-grid">
        <div class="user-activity-chart">
          <h2>User Activity</h2>
          <div class="date-picker">
            <input type="date" v-model="startDate" @change="fetchUserActivity">
            <input type="date" v-model="endDate" @change="fetchUserActivity">
          </div>
          <div v-if="totalUploads !== null" class="total-uploads">
            Total uploads: {{ totalUploads }}
          </div>
          <div ref="chartContainer" style="width: 100%; height: 300px;"></div>
        </div>
        
        <div class="model-management">
          
        </div>
        
        <div class="user-management">
          <h2>User Management</h2>
          <div class="search-bar">
            <input 
              v-model="searchQuery" 
              placeholder="Search by email..." 
              @input="filterUsers"
            />
          </div>
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>First Name</th>
                <th>Last Name</th>
                <th>Roles</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in paginatedUsers" :key="user.username" @click="openUserModal(user)">
                <td>{{ user.username }}</td>
                <td>{{ user.first_name }}</td>
                <td>{{ user.last_name }}</td>
                <td>{{ user.roles }}</td>
              </tr>
            </tbody>
          </table>
          <paginate
            :page-count="pageCount"
            :click-handler="changePage"
            :prev-text="'Prev'"
            :next-text="'Next'"
            container-class="pagination"
            page-class="page-item"
          />
        </div>

        <!-- User Details Modal -->
        <div v-if="selectedUser" class="modal">
          <div class="modal-content">
            <h2>User Details</h2>
            <p><strong>Email:</strong> {{ selectedUser.username }}</p>
            <p><strong>First Name:</strong> {{ selectedUser.first_name }}</p>
            <p><strong>Last Name:</strong> {{ selectedUser.last_name }}</p>
            <div>
              <strong>Role:</strong>
              <select v-model="selectedUser.roles" @change="checkRoleChange">
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select>
            </div>
            <div class="modal-actions">
              <button @click="applyChanges" :disabled="!roleChanged">Apply Changes</button>
              <button @click="confirmDelete">Delete User</button>
              <button @click="closeModal">Close</button>
            </div>
          </div>
        </div>

        <!-- Confirmation Modal -->
        <div v-if="showConfirmation" class="modal">
          <div class="modal-content">
            <h2>Confirm Deletion</h2>
            <p>Are you sure you want to delete this user?</p>
            <div class="modal-actions">
              <button @click="deleteUser">Yes, Delete</button>
              <button @click="cancelDelete">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue';
import axios from 'axios';
import Paginate from "vuejs-paginate-next";
import * as echarts from 'echarts';

export default {
  components: {
    paginate: Paginate,
  },
  setup() {
    const users = ref([]);
    const searchQuery = ref('');
    const currentPage = ref(1);
    const itemsPerPage = 10;
    const selectedUser = ref(null);
    const originalRole = ref('');
    const roleChanged = ref(false);
    const showConfirmation = ref(false);

    const startDate = ref(new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0]);
    const endDate = ref(new Date().toISOString().split('T')[0]);
    const userActivityData = ref([]);
    const totalUploads = ref(null);
    const chartContainer = ref(null);
    const chartInstance = ref(null);

    const fetchUsers = async () => {
      try {
        const response = await axios.get('http://0.0.0.0:8080/auth/users', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('userToken')}`
          }
        });
        users.value = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };

    const filteredUsers = computed(() => {
      const keyword = searchQuery.value.toLowerCase();
      return users.value.filter(user => 
        user.username.toLowerCase().includes(keyword)
      );
    });

    const pageCount = computed(() => {
      return Math.ceil(filteredUsers.value.length / itemsPerPage);
    });

    const paginatedUsers = computed(() => {
      const startIndex = (currentPage.value - 1) * itemsPerPage;
      const endIndex = startIndex + itemsPerPage;
      return filteredUsers.value.slice(startIndex, endIndex);
    });

    const changePage = (page) => {
      currentPage.value = page;
    };

    const filterUsers = () => {
      currentPage.value = 1;
    };

    const openUserModal = (user) => {
      selectedUser.value = { ...user };
      originalRole.value = user.roles;
      roleChanged.value = false;
    };

    const closeModal = () => {
      selectedUser.value = null;
      roleChanged.value = false;
    };

    const checkRoleChange = () => {
      roleChanged.value = selectedUser.value.roles !== originalRole.value;
    };

    const applyChanges = async () => {
      try {
        const encodedUsername = encodeURIComponent(selectedUser.value.username);
        const response = await axios.put(
          `http://0.0.0.0:8080/auth/users/${encodedUsername}/role?new_role=${selectedUser.value.roles}`,
          {},
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('userToken')}`
            }
          }
        );
        console.log('Response:', response.data);
        await fetchUsers();
        closeModal();
      } catch (error) {
        if (error.response) {
          console.error('Error data:', error.response.data);
          console.error('Error status:', error.response.status);
          // 可以根据不同的错误状态码给用户不同的提示
          if (error.response.status === 400) {
            alert(error.response.data.detail);
          } else if (error.response.status === 403) {
            alert("You don't have permission to perform this action.");
          } else if (error.response.status === 404) {
            alert("User not found.");
          } else {
            alert("An error occurred while updating the user role.");
          }
        } else {
          console.error('Error updating user role:', error);
          alert("An unexpected error occurred.");
        }
      }
    };

    const confirmDelete = () => {
      showConfirmation.value = true;
    };

    const cancelDelete = () => {
      showConfirmation.value = false;
    };

    const deleteUser = async () => {
      try {
        await axios.delete(`http://0.0.0.0:8080/auth/users/${selectedUser.value.username}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('userToken')}`
          }
        });
        await fetchUsers();
        showConfirmation.value = false;
        closeModal();
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    };

    //Charts Methods
    const fetchUserActivity = async () => {
      try {
        const response = await axios.get('http://0.0.0.0:8080/file/daily-upload-counts', {
          params: { start_date: startDate.value, end_date: endDate.value },
          headers: { 'Authorization': `Bearer ${localStorage.getItem('userToken')}` }
        });
        userActivityData.value = Object.entries(response.data).map(([date, count]) => ({ date, count }));
        totalUploads.value = userActivityData.value.reduce((sum, item) => sum + item.count, 0);
        await nextTick();
        updateChart();
      } catch (error) {
        console.error('Error fetching user activity:', error);
      }
    };

    const updateChart = () => {
      if (!chartContainer.value) {
        console.error('Chart container not found');
        return;
      }

      if (!chartInstance.value) {
        chartInstance.value = echarts.init(chartContainer.value);
      }

      const option = {
        backgroundColor: 'transparent',
        title: { 
          text: 'Daily File Uploads',
          textStyle: {
            color: '#ffffff'
          }
        },
        tooltip: { 
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderColor: '#8a2be2',
          textStyle: {
            color: '#ffffff'
          }
        },
        xAxis: { 
          type: 'category', 
          data: userActivityData.value.map(item => item.date),
          axisLine: {
            lineStyle: {
              color: '#8a2be2'
            }
          },
          axisLabel: {
            color: '#ffffff'
          }
        },
        yAxis: { 
          type: 'value',
          axisLine: {
            lineStyle: {
              color: '#8a2be2'
            }
          },
          axisLabel: {
            color: '#ffffff'
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(138, 43, 226, 0.2)'
            }
          }
        },
        series: [{
          data: userActivityData.value.map(item => item.count),
          type: 'line',
          smooth: true,
          lineStyle: {
            color: '#8a2be2',
            width: 3
          },
          itemStyle: {
            color: '#8a2be2'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(138, 43, 226, 0.5)' },
              { offset: 1, color: 'rgba(138, 43, 226, 0.1)' }
            ])
          }
        }]
      };

      chartInstance.value.setOption(option);
    };


    onMounted(() => {
      fetchUsers();
      fetchUserActivity();
    });

    return {
      users,
      searchQuery,
      currentPage,
      paginatedUsers,
      pageCount,
      changePage,
      filterUsers,
      selectedUser,
      roleChanged,
      showConfirmation,
      openUserModal,
      closeModal,
      checkRoleChange,
      applyChanges,
      confirmDelete,
      cancelDelete,
      deleteUser,
      startDate,
      endDate,
      totalUploads,
      fetchUserActivity,
      chartContainer,
    };
  }
}
</script>

<style scoped>
@import "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css";

.admin-dashboard {
  font-family: Arial, sans-serif;
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
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

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  position: relative;
  z-index: 1;
}

.logo {
  flex: 0 0 auto;
}

.logo-image {
  max-height: 50px;
  width: auto;
}

.nav-links {
  display: flex;
  list-style-type: none;
  margin: 0;
  padding: 0;
  flex: 1 1 auto;
  justify-content: flex-start;
  margin-left: 20px;
}

.nav-links li {
  margin-right: 1rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
}

.register-btn {
  flex: 0 0 auto;
  background-color: #8a2be2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
}

.dashboard-content {
  padding: 20px;
  position: relative;
  z-index: 1;
  color: white;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.user-activity-chart, .model-management, .user-management, .model-performance {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.tab-header button {
  background: none;
  border: none;
  padding: 10px;
  cursor: pointer;
  color: white;
}

.tab-header button.active {
  border-bottom: 2px solid #8a2be2;
}

.search-bar {
  margin-bottom: 15px;
}

.search-bar input {
  width: 90%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

table {
  width: 100%;
  border-collapse: collapse;
  color: white;
}

th, td {
  text-align: left;
  padding: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.pagination {
  display: flex;
  justify-content: center;
  list-style-type: none;
  padding: 0;
  margin-top: 20px;
}

.page-item {
  margin: 0 5px;
}

.page-item a {
  padding: 5px 10px;
  border: 1px solid #8a2be2;
  border-radius: 3px;
  text-decoration: none;
  color: white;
  background-color: rgba(138, 43, 226, 0.2);
}

.page-item.active a {
  background-color: #8a2be2;
  color: white;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2;
}

.modal-content {
  background-color: #24243e;
  padding: 20px;
  border-radius: 5px;
  max-width: 500px;
  width: 100%;
  color: white;
}

.modal-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

button {
  padding: 5px 10px;
  cursor: pointer;
  background-color: #8a2be2;
  color: white;
  border: none;
  border-radius: 3px;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.date-picker {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.date-picker input {
  padding: 5px;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid #8a2be2;
  border-radius: 3px;
}

.total-uploads {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
}
</style>