// Estrelas animadas no fundo
const canvas = document.getElementById('stars-canvas'); // Seleciona o elemento <canvas> com ID 'stars-canvas'
const ctx = canvas.getContext('2d'); // Pega o contexto 2D para desenhar no canvas

// Ajusta o tamanho do canvas para cobrir toda a janela
function resizeCanvas() {
  canvas.width = window.innerWidth;  // Largura do canvas igual à largura da janela
  canvas.height = window.innerHeight; // Altura do canvas igual à altura da janela
}
resizeCanvas(); // Chama a função uma vez ao carregar o script

let stars = []; // Array que vai guardar as estrelas
const numStars = 100; // Quantidade total de estrelas

// Gera as estrelas com posições, tamanhos e velocidades aleatórias
for (let i = 0; i < numStars; i++) {
  stars.push({
    x: Math.random() * canvas.width,       // Posição horizontal aleatória
    y: Math.random() * canvas.height,      // Posição vertical aleatória
    radius: Math.random() * 1.5,           // Raio pequeno aleatório
    velocity: Math.random() * 0.5 + 0.2    // Velocidade de subida (mínimo 0.2)
  });
}

// Desenha todas as estrelas no canvas
function drawStars() {
  ctx.clearRect(0, 0, canvas.width, canvas.height); // Limpa o canvas antes de redesenhar
  ctx.fillStyle = '#ffffff'; // Cor branca para as estrelas
  for (let star of stars) {
    ctx.beginPath(); // Começa um novo caminho
    ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2); // Desenha um círculo (estrela)
    ctx.fill(); // Preenche o círculo
  }
}

// Atualiza a posição das estrelas para fazer o efeito de movimento
function updateStars() {
  for (let star of stars) {
    star.y -= star.velocity; // Move a estrela para cima
    if (star.y < 0) { // Se sair da parte de cima da tela...
      star.y = canvas.height; // ...recomeça na parte inferior
      star.x = Math.random() * canvas.width; // ...com uma nova posição horizontal
    }
  }
}

// Loop de animação contínuo
function animateStars() {
  drawStars();        // Desenha as estrelas
  updateStars();      // Atualiza suas posições
  requestAnimationFrame(animateStars); // Chama a si mesmo para continuar o loop
}
animateStars(); // Inicia a animação

// Reajusta o canvas se a janela for redimensionada
window.addEventListener('resize', resizeCanvas);

// Mostrar nome do arquivo selecionado
document.getElementById('imagem').addEventListener('change', function () {
  const nomeArquivo = this.files[0] ? this.files[0].name : 'Nenhum arquivo selecionado'; // Pega o nome do arquivo ou texto padrão
  document.getElementById('nome-arquivo').textContent = nomeArquivo; // Mostra o nome no elemento correspondente
});

// Atualizar e desenhar a grade de cortes
function atualizarGrade() {
  const gridOverlay = document.querySelector('.grid-overlay'); // Seleciona a camada da grade
  const rowsInput = document.getElementById('rows'); // Campo de linhas
  const colsInput = document.getElementById('cols'); // Campo de colunas

  if (!gridOverlay || !rowsInput || !colsInput) return; // Se algum elemento não existir, sai da função

  const rows = parseInt(rowsInput.value) || 1; // Número de linhas, padrão = 1
  const cols = parseInt(colsInput.value) || 1; // Número de colunas, padrão = 1

  // Atualiza variáveis CSS personalizadas para controlar o layout da grade
  gridOverlay.style.setProperty('--rows', rows);
  gridOverlay.style.setProperty('--cols', cols);

  // Limpa qualquer grade anterior
  gridOverlay.innerHTML = '';

  // Cria e adiciona os blocos da nova grade
  for (let i = 0; i < rows * cols; i++) {
    const div = document.createElement('div'); // Cria uma célula
    gridOverlay.appendChild(div); // Adiciona à sobreposição da grade
  }
}

// Atualiza a grade ao carregar a página
window.addEventListener('load', atualizarGrade);

// Atualiza a grade quando os inputs de linhas ou colunas mudam
document.getElementById('rows').addEventListener('input', atualizarGrade);
document.getElementById('cols').addEventListener('input', atualizarGrade);