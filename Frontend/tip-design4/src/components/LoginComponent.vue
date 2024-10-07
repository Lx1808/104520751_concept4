<template>
  <div class="login-container">
    <nav class="top-nav">
      <div class="logo"><!-- Add your logo here --></div>
      <ul>
        <li><a href="#">Home</a></li>
        <li><a href="#">About</a></li>
        <li><a href="#">Blog</a></li>
        <li><a href="#">Contact</a></li>
      </ul>
      <button class="register-btn" @click="showRegistrationModal = true">Register</button>
    </nav>
    
    <main>
      <h1>Welcome to<br>Peace of Mind</h1>
      <p>sign in to learn more</p>
      
      <form @submit.prevent="handleSubmit">
        <div class="input-group">
          <input type="email" v-model="email" placeholder="Enter Email">
          <button type="button" class="clear-btn" @click="email = ''">×</button>
        </div>
        <div class="input-group">
          <input type="password" v-model="password" placeholder="Password">
          <button type="button" class="toggle-password" @click="togglePasswordVisibility">
            <!-- Add eye icon here -->
          </button>
        </div>
        <a href="#" class="forgot-password">Recover Password ?</a>
        <button type="submit" class="submit-btn">Sign In</button>
      </form>
    </main>

    <!-- Register -->
    <div v-if="showRegistrationModal" class="modal">
      <div class="modal-content">
        <span class="close-btn" @click="showRegistrationModal = false">&times;</span>
        <h2>User Registration</h2>
        <form @submit.prevent="register">
          <div class="input-group">
            <input type="text" v-model="firstName" placeholder="First name">
            <input type="text" v-model="lastName" placeholder="Last name">
          </div>
          <div class="input-group">
            <input type="email" v-model="email" placeholder="Email">
          </div>
          <div class="input-group">
            <input type="password" v-model="password" placeholder="Password">
            <input type="password" v-model="confirmPassword" placeholder="Re-enter Password">
          </div>
          <button type="submit" class="submit-btn">Register</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      email: '',
      password: '',
      firstName: '',
      lastName: '',
      confirmPassword: '',
      roles: 'user',
      showPassword: false,
      isLoading: false,
      errorMessage: '',
      showRegistrationModal: false
    }
  },
  methods: {
    closeModal() {
      this.showRegistrationModal = false; // 关闭模态框
    },
    async register() {
      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match!";
        return;
      }
      
      try {
        const response = await axios.post('http://0.0.0.0:8080/auth/register', {
          username: this.email, // 将 email 作为 username
          password: this.password,
          first_name: this.firstName,
          last_name: this.lastName,
          roles: this.roles
        });

        // 如果注册成功，关闭模态框或重定向
        this.closeModal();
        alert(response.data.message || 'User registered successfully!');

      } catch (error) {
        // 处理错误
        if (error.response) {
          // 服务器返回的错误
          this.errorMessage = error.response.data.detail || '注册失败，请重试。';
        } else {
          // 网络错误等
          this.errorMessage = '无法连接到服务器，请稍后再试。';
        }
      }
    },
    async handleSubmit() {
      this.isLoading = true;
      this.errorMessage = '';

      try {
        // 使用 FormData 发送表单数据
        const formData = new FormData();
        formData.append('username', this.email);  // 这里需要是 username
        formData.append('password', this.password); // 这里保持 password

        const response = await axios.post('http://0.0.0.0:8080/auth/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded', // 确保请求类型为表单
          },
        });

        const token = response.data.access_token;

        // 将 token 存储在 localStorage 中
        localStorage.setItem('userToken', token);

        // 获取用户信息
        const userInfoResponse = await axios.get('http://0.0.0.0:8080/auth/users/me', {
          headers: { Authorization: `Bearer ${token}` }
        });

        const userInfo = userInfoResponse.data;
        localStorage.setItem('userInfo', JSON.stringify(userInfo));

        // 根据用户角色跳转
        if (userInfo.roles.includes('admin')) {
          this.$router.push('/admin-dashboard');
        } else {
          this.$router.push('/user-dashboard');
        }
      } catch (error) {
        if (error.response) {
          this.errorMessage = error.response.data.message || '登录失败，请检查您的凭证。';
        } else if (error.request) {
          this.errorMessage = '无法连接到服务器，请稍后再试。';
        } else {
          this.errorMessage = '发生错误，请稍后再试。';
        }
      } finally {
        this.isLoading = false;
      }
    },
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword
    }
  }
}
</script>

<style scoped>
.login-container {
  font-family: Arial, sans-serif;
  background: linear-gradient(to bottom right, #ffffff, #e6e6fa);
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  position: relative;
}

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

.register-btn {
  background-color: #8a2be2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
}

main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  width: 100vw;
  padding: 0;
}

h1 {
  color: #8a2be2;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

form {
  width: 100%;
  max-width: 400px; /* Optional to limit width of form */
  margin-top: 2rem;
  padding: 0 20px; /* Optional for padding */
}

.input-group {
  position: relative;
  margin-bottom: 1rem;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d3d3d3;
  border-radius: 5px;
}

.clear-btn, .toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
}

.forgot-password {
  display: block;
  text-align: right;
  margin-bottom: 1rem;
  color: #8a2be2;
  text-decoration: none;
}

.submit-btn {
  width: 100%;
  background-color: #8a2be2;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 5px;
  cursor: pointer;
}

.error-message {
  color: red;
  margin-top: 1rem;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  text-align: center;
}

.close-btn {
  float: right;
  font-size: 24px;
  cursor: pointer;
}

.input-group {
  margin: 10px 0;
  display: flex;
  gap: 10px;
}

.submit-btn {
  width: 100%;
  background-color: #8a2be2;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 5px;
  cursor: pointer;
}

h2 {
  color: #8a2be2;
  margin-bottom: 20px;
}

</style>