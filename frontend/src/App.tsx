import { useState } from 'react'
import LoginPage from './components/LoginPage.tsx'  // Agrega .tsx
import './App.css'

function App() {
  const [isLogin, setIsLogin] = useState(true);

  const toggleMode = () => {
    setIsLogin(!isLogin);
  };

  return (
    <div className="App">
      <LoginPage onToggleMode={toggleMode} isLogin={isLogin} />
    </div>
  )
}

export default App