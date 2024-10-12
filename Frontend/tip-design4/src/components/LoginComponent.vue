<template>
  <div class="login-container space-background">
    <nav class="top-nav">
      <div class="logo">
        <img src="/Users/lixiang/Documents/COS70008/Project/Frontend/tip-design4/public/FaceLogo.png" alt="Logo" class="logo-image">
      </div>
      <ul class="nav-links">
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

    <!-- Register Modal -->
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
// Script remains unchanged
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
      this.showRegistrationModal = false;
    },
    async register() {
      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match!";
        return;
      }
      
      try {
        const response = await axios.post('http://0.0.0.0:8080/auth/register', {
          username: this.email,
          password: this.password,
          first_name: this.firstName,
          last_name: this.lastName,
          roles: this.roles
        });

        this.closeModal();
        alert(response.data.message || 'User registered successfully!');

      } catch (error) {
        if (error.response) {
          this.errorMessage = error.response.data.detail || 'Registration failed, please try again.';
        } else {
          this.errorMessage = 'Unable to connect to server, please try again later.';
        }
      }
    },
    async handleSubmit() {
      this.isLoading = true;
      this.errorMessage = '';

      try {
        const formData = new FormData();
        formData.append('username', this.email);
        formData.append('password', this.password);

        const response = await axios.post('http://0.0.0.0:8080/auth/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        });

        const token = response.data.access_token;
        localStorage.setItem('userToken', token);

        const userInfoResponse = await axios.get('http://0.0.0.0:8080/auth/users/me', {
          headers: { Authorization: `Bearer ${token}` }
        });

        const userInfo = userInfoResponse.data;
        localStorage.setItem('userInfo', JSON.stringify(userInfo));

        if (userInfo.roles.includes('admin')) {
          this.$router.push('/admin-dashboard');
        } else {
          this.$router.push('/user-dashboard');
        }
      } catch (error) {
        if (error.response) {
          this.errorMessage = error.response.data.message || 'Login failed, please check your credentials.';
        } else if (error.request) {
          this.errorMessage = 'Unable to connect to server, please try again later.';
        } else {
          this.errorMessage = 'An error occurred, please try again later.';
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
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  position: relative;
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
  flex: 0 0 auto; /* Prevents the logo from growing or shrinking */
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
  flex: 1 1 auto; /* Allows the nav links to grow and shrink */
  justify-content: flex-start; /* Aligns items to the start of the container */
  margin-left: 20px; /* Adds some space between the logo and nav links */
}

.nav-links li {
  margin-right: 1rem;
}

.nav-links li:last-child {
  margin-right: 0;
}

.nav-links a {
  color: white;
  text-decoration: none;
}

.register-btn {
  flex: 0 0 auto; /* Prevents the button from growing or shrinking */
  background-color: #8a2be2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
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

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  position: relative;
  z-index: 1;
}

nav ul {
  display: flex;
  list-style-type: none;
}

nav ul li {
  margin-right: 1rem;
}

nav ul li a {
  color: white;
  text-decoration: none;
}

.register-btn {
  background-color: #8a2be2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
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
  position: relative;
  z-index: 1;
}

h1 {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

p {
  color: #cccccc;
}

form {
  width: 100%;
  max-width: 400px;
  margin-top: 2rem;
  padding: 0 20px;
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
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

input::placeholder {
  color: #cccccc;
}

.clear-btn, .toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: white;
}

.forgot-password {
  display: block;
  text-align: right;
  margin-bottom: 1rem;
  color: #cccccc;
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
  color: #ff6b6b;
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
  z-index: 2;
}

.modal-content {
  background-color: #24243e;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  text-align: center;
  color: white;
}

.close-btn {
  float: right;
  font-size: 24px;
  cursor: pointer;
  color: white;
}

h2 {
  color: #8a2be2;
  margin-bottom: 20px;
}
</style>