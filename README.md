## Click Auto (simples)

Programa Python simples que permite configurar um intervalo (em segundos) e clicar automaticamente na posição do mouse definida.

Requisitos
- Python 3.8+
- Instalar dependências: `pip install -r requirements.txt`

Uso
1. Abra o programa: `python main.py`
2. Defina o intervalo em segundos.
3. Clique em "Definir posição" com o mouse na posição desejada (ou permita que o programa capture a posição atual ao iniciar).
4. Clique em "Iniciar" para começar os cliques automáticos e em "Parar" para interromper.

Hotkeys
- `F8`: Pausar / Retomar (não precisa usar o botão "Parar")
- `F9`: Definir a posição atual do mouse (útil enquanto o programa está em execução)

Opções
- `Seguir mouse`: quando ativado, o programa usa a posição atual do mouse a cada clique, permitindo que você mova o ponteiro enquanto o auto-clicker está ativo.
- `Adicionar local atual`: permite configurar vários pontos de clique diferentes, cada um com seu próprio intervalo.

Novidade nesta branch `20260501`
- Agora você pode adicionar vários locais de clique.
- Cada local pode usar um intervalo específico ou herdar o intervalo padrão.
- O loop percorre os locais em sequência, clicando em cada um.
- Botão "Limpar lista" para remover todos os locais de uma vez.
- Correções: Foco automático ao pausar, prevenção de duplicatas e debounce para evitar adições múltiplas.
- Testes unitários criados para validar a lógica.

Compilação para Executável
Para criar um executável standalone no Windows:
1. Instale PyInstaller: `pip install pyinstaller`
2. Execute: `pyinstaller --onefile --noconsole main.py`
3. O executável será gerado em `dist/main.exe`

Observações
- No Windows pode ser necessário executar em modo normal (não requer privilégios elevados na maioria dos casos).
- Para interromper rapidamente, feche o programa.
