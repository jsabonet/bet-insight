/**
 * Gera uma imagem placeholder blur SVG para usar enquanto a imagem real carrega
 * Melhora Core Web Vitals (CLS - Cumulative Layout Shift)
 */
export const generateBlurPlaceholder = (width = 400, height = 300, color = '#e5e7eb') => {
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:${color};stop-opacity:1" />
          <stop offset="100%" style="stop-color:${adjustBrightness(color, -20)};stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="${width}" height="${height}" fill="url(#grad)"/>
    </svg>
  `;
  
  return `data:image/svg+xml;base64,${btoa(svg)}`;
};

/**
 * Ajusta o brilho de uma cor hex
 */
const adjustBrightness = (hex, percent) => {
  const num = parseInt(hex.replace('#', ''), 16);
  const amt = Math.round(2.55 * percent);
  const R = (num >> 16) + amt;
  const G = (num >> 8 & 0x00FF) + amt;
  const B = (num & 0x0000FF) + amt;
  
  return '#' + (
    0x1000000 +
    (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
    (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
    (B < 255 ? (B < 1 ? 0 : B) : 255)
  ).toString(16).slice(1);
};

/**
 * Gera srcset para imagens responsivas
 * Melhora performance em diferentes resoluções
 */
export const generateSrcSet = (baseUrl, sizes = [320, 640, 960, 1280]) => {
  return sizes
    .map(size => {
      const url = baseUrl.replace(/\.(jpg|png|webp)$/, `_${size}w.$1`);
      return `${url} ${size}w`;
    })
    .join(', ');
};

/**
 * Otimiza URL de imagem para diferentes formatos
 */
export const optimizeImageUrl = (url, options = {}) => {
  const {
    width,
    height,
    quality = 80,
    format = 'auto'
  } = options;
  
  // Se estiver usando um CDN como Cloudinary ou imgix, adicione os parâmetros
  // Exemplo para Cloudinary:
  // return url.replace('/upload/', `/upload/w_${width},h_${height},q_${quality},f_${format}/`);
  
  // Por enquanto, retorna a URL original
  // Você pode integrar com CDN posteriormente
  return url;
};

/**
 * Carrega imagem com fallback
 */
export const loadImageWithFallback = (src, fallback) => {
  return new Promise((resolve) => {
    const img = new Image();
    
    img.onload = () => resolve(src);
    img.onerror = () => resolve(fallback);
    
    img.src = src;
  });
};

/**
 * Preload de imagens críticas
 * Usar para imagens above-the-fold
 */
export const preloadImage = (src) => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = 'image';
  link.href = src;
  document.head.appendChild(link);
};

/**
 * Lazy load de imagens com Intersection Observer
 */
export const lazyLoadImages = (selector = 'img[data-src]') => {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          observer.unobserve(img);
        }
      });
    }, {
      rootMargin: '50px' // Carrega 50px antes de entrar na viewport
    });

    document.querySelectorAll(selector).forEach(img => {
      imageObserver.observe(img);
    });
  } else {
    // Fallback para navegadores sem suporte
    document.querySelectorAll(selector).forEach(img => {
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
    });
  }
};

/**
 * Comprime imagem no client-side antes do upload
 */
export const compressImage = async (file, maxWidth = 1920, quality = 0.8) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const img = new Image();
      
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        
        // Redimensiona se necessário
        if (width > maxWidth) {
          height = (height * maxWidth) / width;
          width = maxWidth;
        }
        
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob(
          (blob) => {
            resolve(new File([blob], file.name, {
              type: 'image/jpeg',
              lastModified: Date.now()
            }));
          },
          'image/jpeg',
          quality
        );
      };
      
      img.src = e.target.result;
    };
    
    reader.readAsDataURL(file);
  });
};

export default {
  generateBlurPlaceholder,
  generateSrcSet,
  optimizeImageUrl,
  loadImageWithFallback,
  preloadImage,
  lazyLoadImages,
  compressImage
};
