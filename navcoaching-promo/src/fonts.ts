import "@fontsource/readex-pro/arabic-300.css";
import "@fontsource/readex-pro/arabic-400.css";
import "@fontsource/readex-pro/arabic-500.css";
import "@fontsource/readex-pro/arabic-600.css";
import "@fontsource/readex-pro/arabic-700.css";
import "@fontsource/readex-pro/latin-300.css";
import "@fontsource/readex-pro/latin-400.css";
import "@fontsource/readex-pro/latin-500.css";
import "@fontsource/readex-pro/latin-600.css";
import "@fontsource/readex-pro/latin-700.css";
import "@fontsource/jetbrains-mono/latin-400.css";
import "@fontsource/jetbrains-mono/latin-700.css";
import { continueRender, delayRender } from "remotion";

// Font files are bundled locally; block rendering until every face is ready
// so no frame is ever captured with a fallback font.
const handle = delayRender("fonts");
const faces = [300, 400, 500, 600, 700].flatMap((w) => [
  `${w} 64px "Readex Pro"`,
]);
Promise.all([
  ...faces.map((f) => document.fonts.load(f, "تدريب Nav")),
  ...faces.map((f) => document.fonts.load(f, "Coaching 0123")),
  document.fonts.load(`400 32px "JetBrains Mono"`, "NAV 01"),
  document.fonts.load(`700 32px "JetBrains Mono"`, "NAV 01"),
])
  .then(() => document.fonts.ready)
  .then(() => continueRender(handle))
  .catch((e) => {
    console.error(e);
    continueRender(handle);
  });
