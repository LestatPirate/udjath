# MonitorRes

Aplicação de barra de menu para macOS que permite mudar a resolução do ecrã (interno ou externo) para as resoluções mais comuns — incluindo resoluções ultrawide como **3440x1440** — com confirmação automática: se não confirmares a nova resolução dentro de alguns segundos, a app reverte sozinha para a resolução anterior (tal como o próprio macOS faz ao mudar de resolução em Definições > Ecrãs).

Escrita em Python, corre localmente, sem dependências de rede nem serviços externos.

## Funcionalidades

- Ícone na barra de menu (sem ícone no Dock) com a lista de ecrãs ligados e as respetivas resoluções disponíveis.
- Lista de resoluções comuns pré-definida (1920x1080, 2560x1440, 3440x1440, 3840x2160, entre outras) — as que o ecrã atual não suporta aparecem desativadas.
- Expõe resoluções HiDPI/escaladas que o macOS esconde por defeito em Definições > Ecrãs (a mesma técnica usada por ferramentas como o SwitchResX).
- Confirmação com contagem decrescente após aplicar uma resolução: se não confirmares, reverte automaticamente.
- Notificações do sistema a confirmar a mudança ou o revert.

## Renomear um ecrã (permanente, ao nível do sistema)

Cada ecrã tem uma opção **"Renomear este ecrã..."** que grava um nome novo na base de overrides de ecrãs do macOS (`/Library/Displays/Contents/Resources/Overrides/`) — o mesmo mecanismo usado por ferramentas como o SwitchResX. Ao contrário da troca de resolução, isto:

- Pede a palavra-passe de administrador (a app usa `osascript ... with administrator privileges`, que mostra o diálogo de autenticação nativo do macOS — a app nunca vê nem guarda a palavra-passe).
- Só tem efeito depois de desligares e voltares a ligar o cabo do monitor, ou de terminares sessão — o macOS só lê esta base de dados quando o ecrã liga, não continuamente.
- É permanente e visível em Definições > Ecrãs, para qualquer app e depois de reiniciar.

## Limitações conhecidas

- Só expõe resoluções que o macOS considera tecnicamente suportadas para o ecrã ligado (nativas ou variantes HiDPI escaladas da resolução nativa). Não força resoluções que o monitor não anuncia como suportadas via EDID — isso não é fiável em nenhum monitor/driver e pode resultar em ecrã preto.
- Não existe forma de reduzir o tamanho aparente dos elementos da interface (texto, ícones) abaixo do limite físico de 1 ponto = 1 pixel do painel, sem perder nitidez — isto é uma limitação de densidade de pixels do monitor, não de software.

## Requisitos

- macOS
- Python 3.9+

## Instalação / build

```bash
git clone https://github.com/LestatPirate/MonitorRes.git
cd MonitorRes
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python3 setup.py py2app
```

Isto gera `dist/MonitorRes.app`. Como não está assinado, da primeira vez que abrires o macOS vai bloquear — clica com o botão direito no `.app` → **Abrir** → **Abrir** (só é preciso uma vez). Depois podes copiar o `.app` para `/Applications`.

Para correr diretamente sem empacotar (útil durante desenvolvimento):

```bash
./venv/bin/python3 app.py
```

## Como funciona

- [`display_manager.py`](display_manager.py) — usa o CoreGraphics (via PyObjC/Quartz) para listar ecrãs e resoluções, e para aplicar uma nova resolução com `CGConfigureDisplayWithDisplayMode`.
- [`display_naming.py`](display_naming.py) — gera e instala o plist de override do nome do ecrã, pedindo autorização de administrador via `osascript`.
- [`confirm_dialog.py`](confirm_dialog.py) — diálogos com `NSAlert`: confirmação com `NSTimer` (contagem decrescente com revert automático) e um prompt de texto simples para o nome novo do ecrã.
- [`known_resolutions.py`](known_resolutions.py) — lista de resoluções comuns mostradas no menu.
- [`app.py`](app.py) — a app de barra de menu (usa [rumps](https://github.com/jaredks/rumps)).
- [`setup.py`](setup.py) — script de build (`py2app`) para gerar o `.app` final.

## Licença

[MIT](LICENSE)
