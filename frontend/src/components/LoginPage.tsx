import React, { useState } from 'react';
import { Eye, EyeOff, Mail, Lock, User, LogIn, UserPlus, Shield } from 'lucide-react';

interface LoginPageProps {
  onToggleMode: () => void;
  isLogin?: boolean;
}

const LoginPage: React.FC<LoginPageProps> = ({ onToggleMode, isLogin = true }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!isLogin && !formData.name.trim()) {
      newErrors.name = 'El nombre es requerido';
    } else if (!isLogin && formData.name.length < 2) {
      newErrors.name = 'El nombre debe tener al menos 2 caracteres';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'El correo es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'El correo no es válido';
    }

    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (!isLogin && formData.password.length < 8) {
      newErrors.password = 'La contraseña debe tener al menos 8 caracteres';
    } else if (!isLogin) {
      const hasUpper = /[A-Z]/.test(formData.password);
      const hasLower = /[a-z]/.test(formData.password);
      const hasNumber = /\d/.test(formData.password);

      if (!hasUpper || !hasLower || !hasNumber) {
        newErrors.password = 'La contraseña debe tener al menos una mayúscula, una minúscula y un número';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      alert(isLogin ? 'Inicio de sesión exitoso' : 'Registro exitoso');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-snow-white flex items-center justify-center p-4">
      <div className="relative w-full max-w-md">
        <div className="bg-creamy-vanilla rounded-2xl p-8 shadow-2xl border border-olive-green/20">
          {/* Logo/Header */}
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-olive-green rounded-2xl flex items-center justify-center mb-4 shadow-lg">
              <Shield className="w-8 h-8 text-snow-white" />
            </div>
            <h1 className="text-3xl font-bold text-salsa-tomato mb-2">
              {isLogin ? 'Bienvenido' : 'Crear Cuenta'}
            </h1>
            <p className="text-ash-gray">
              {isLogin ? 'Inicia sesión en tu cuenta' : 'Regístrate para comenzar'}
            </p>
          </div>

          {/* Form */}npm install

          <div className="space-y-6">
            {!isLogin && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-charcoal-gray block">
                  Nombre completo
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-olive-green w-5 h-5" />
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className={`w-full pl-12 pr-4 py-3 bg-snow-white border ${
                      errors.name ? 'border-red-400' : 'border-olive-green/30'
                    } rounded-xl text-charcoal-gray placeholder-ash-gray focus:outline-none focus:border-salsa-tomato transition-all duration-200`}
                    placeholder="Tu nombre completo"
                  />
                </div>
                {errors.name && (
                  <p className="text-red-500 text-sm">{errors.name}</p>
                )}
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-charcoal-gray block">
                Correo electrónico
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-olive-green w-5 h-5" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={`w-full pl-12 pr-4 py-3 bg-snow-white border ${
                    errors.email ? 'border-red-400' : 'border-olive-green/30'
                  } rounded-xl text-charcoal-gray placeholder-ash-gray focus:outline-none focus:border-salsa-tomato transition-all duration-200`}
                  placeholder="tu@email.com"
                />
              </div>
              {errors.email && (
                <p className="text-red-500 text-sm">{errors.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-charcoal-gray block">
                Contraseña
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-olive-green w-5 h-5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`w-full pl-12 pr-12 py-3 bg-snow-white border ${
                    errors.password ? 'border-red-400' : 'border-olive-green/30'
                  } rounded-xl text-charcoal-gray placeholder-ash-gray focus:outline-none focus:border-salsa-tomato transition-all duration-200`}
                  placeholder={isLogin ? 'Tu contraseña' : 'Mínimo 8 caracteres'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-olive-green hover:text-salsa-tomato transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-500 text-sm">{errors.password}</p>
              )}
            </div>

            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="w-full bg-salsa-tomato hover:bg-olive-green text-snow-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
              ) : (
                <>
                  {isLogin ? <LogIn className="w-5 h-5" /> : <UserPlus className="w-5 h-5" />}
                  <span>{isLogin ? 'Iniciar Sesión' : 'Crear Cuenta'}</span>
                </>
              )}
            </button>
          </div>

          {/* Toggle mode */}
          <div className="mt-8 text-center">
            <p className="text-ash-gray">
              {isLogin ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?'}
            </p>
            <button
              onClick={onToggleMode}
              className="text-olive-green hover:text-salsa-tomato font-semibold underline mt-1 transition-colors"
            >
              {isLogin ? 'Regístrate aquí' : 'Inicia sesión aquí'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
