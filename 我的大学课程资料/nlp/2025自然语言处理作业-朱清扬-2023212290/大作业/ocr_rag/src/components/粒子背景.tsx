import { useEffect, useRef } from "react";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  hue: number;
  pulseSpeed: number;
}

interface FloatingOrb {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  hue: number;
  saturation: number;
  lightness: number;
  opacity: number;
  pulsePhase: number;
}

export function 粒子背景() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const orbsRef = useRef<FloatingOrb[]>([]);
  const animationIdRef = useRef<number>();
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const createParticles = () => {
      const particleCount = Math.floor((canvas.width * canvas.height) / 10000);
      particlesRef.current = [];

      for (let i = 0; i < particleCount; i++) {
        particlesRef.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          size: Math.random() * 2.5 + 0.5,
          opacity: Math.random() * 0.12 + 0.04,
          hue: 0, // 使用灰色调
          pulseSpeed: Math.random() * 0.02 + 0.01,
        });
      }
    };

    const createOrbs = () => {
      const orbCount = 4;
      orbsRef.current = [];

      for (let i = 0; i < orbCount; i++) {
        orbsRef.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
          radius: Math.random() * 180 + 100,
          hue: 0, // 灰色调
          saturation: 0, // 无饱和度
          lightness: Math.random() * 20 + 70, // 中灰色
          opacity: Math.random() * 0.06 + 0.03,
          pulsePhase: Math.random() * Math.PI * 2,
        });
      }
    };

    const updateParticles = () => {
      timeRef.current += 0.016;

      particlesRef.current.forEach(particle => {
        particle.x += particle.vx;
        particle.y += particle.vy;

        // 边界循环
        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;

        // 脉动效果
        particle.opacity = Math.sin(timeRef.current * particle.pulseSpeed) * 0.06 + 0.12;
      });

      orbsRef.current.forEach(orb => {
        orb.x += orb.vx;
        orb.y += orb.vy;

        // 边界反弹
        if (orb.x < -orb.radius || orb.x > canvas.width + orb.radius) {
          orb.vx *= -1;
        }
        if (orb.y < -orb.radius || orb.y > canvas.height + orb.radius) {
          orb.vy *= -1;
        }

        // 脉动
        orb.pulsePhase += 0.02;
        orb.opacity = Math.sin(orb.pulsePhase) * 0.04 + 0.1;
      });
    };

    const drawBackground = () => {
      // 创建柔和的径向渐变背景
      const gradient = ctx.createRadialGradient(
        canvas.width / 2, canvas.height / 2, 0,
        canvas.width / 2, canvas.height / 2, Math.max(canvas.width, canvas.height) / 2
      );
      gradient.addColorStop(0, 'rgba(156, 163, 175, 0.02)');
      gradient.addColorStop(0.5, 'rgba(107, 114, 128, 0.03)');
      gradient.addColorStop(1, 'rgba(75, 85, 99, 0.04)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    };

    const drawOrbs = () => {
      orbsRef.current.forEach(orb => {
        const gradient = ctx.createRadialGradient(orb.x, orb.y, 0, orb.x, orb.y, orb.radius);
        gradient.addColorStop(0, `hsla(${orb.hue}, ${orb.saturation}%, ${orb.lightness}%, ${orb.opacity})`);
        gradient.addColorStop(0.4, `hsla(${orb.hue}, ${orb.saturation}%, ${orb.lightness}%, ${orb.opacity * 0.5})`);
        gradient.addColorStop(1, `hsla(${orb.hue}, ${orb.saturation}%, ${orb.lightness}%, 0)`);

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(orb.x, orb.y, orb.radius, 0, Math.PI * 2);
        ctx.fill();
      });
    };

    const drawParticles = () => {
      particlesRef.current.forEach(particle => {
        ctx.save();
        ctx.globalAlpha = particle.opacity;
        
        // 创建柔和发光效果
        ctx.shadowBlur = 6;
        ctx.shadowColor = 'rgba(156, 163, 175, 0.4)';
        
        ctx.fillStyle = 'rgba(156, 163, 175, 0.7)';
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      // 绘制连接线
      particlesRef.current.forEach((particle, i) => {
        particlesRef.current.slice(i + 1).forEach(otherParticle => {
          const dx = particle.x - otherParticle.x;
          const dy = particle.y - otherParticle.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 120) {
            ctx.save();
            const alpha = (120 - distance) / 120 * 0.08;
            ctx.globalAlpha = alpha;
            
            ctx.strokeStyle = 'rgba(156, 163, 175, 0.5)';
            ctx.lineWidth = 0.8;
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(otherParticle.x, otherParticle.y);
            ctx.stroke();
            ctx.restore();
          }
        });
      });
    };

    const drawGrid = () => {
      ctx.save();
      ctx.globalAlpha = 0.025;
      ctx.strokeStyle = 'rgba(156, 163, 175, 0.6)';
      ctx.lineWidth = 0.4;
      
      const gridSize = 100;
      
      // 垂直线
      for (let x = 0; x <= canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      
      // 水平线
      for (let y = 0; y <= canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }
      
      ctx.restore();
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      drawBackground();
      drawGrid();
      drawOrbs();
      updateParticles();
      drawParticles();
      
      animationIdRef.current = requestAnimationFrame(animate);
    };

    resizeCanvas();
    createParticles();
    createOrbs();
    animate();

    const handleResize = () => {
      resizeCanvas();
      createParticles();
      createOrbs();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ background: 'transparent' }}
    />
  );
}