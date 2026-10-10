import { Fragment } from "react";

const SAFE_HREF = /^(https?:\/\/|mailto:)/i;

function emphasize(text, keyBase) {
  const nodes = [];
  const re = /(\*\*([^*]+)\*\*)|(__([^_]+)__)|(\*([^*]+)\*)|(_([^_]+)_)/g;
  let last = 0;
  let m;
  let i = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    if (m[2] !== undefined || m[4] !== undefined) {
      nodes.push(<strong key={`${keyBase}-s${i}`}>{m[2] ?? m[4]}</strong>);
    } else {
      nodes.push(<em key={`${keyBase}-e${i}`}>{m[6] ?? m[8]}</em>);
    }
    i++;
    last = m.index + m[0].length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

function renderInline(text, keyBase) {
  const out = [];
  let key = 0;
  String(text)
    .split(/(`[^`]+`)/g)
    .forEach((part) => {
      if (/^`[^`]+`$/.test(part)) {
        out.push(<code key={`${keyBase}-c${key++}`}>{part.slice(1, -1)}</code>);
        return;
      }
      const linkRe = /\[([^\]]+)\]\(([^)\s]+)\)/g;
      let last = 0;
      let m;
      const pieces = [];
      while ((m = linkRe.exec(part))) {
        if (m.index > last) pieces.push({ t: "text", v: part.slice(last, m.index) });
        pieces.push({ t: "link", label: m[1], href: m[2] });
        last = m.index + m[0].length;
      }
      if (last < part.length) pieces.push({ t: "text", v: part.slice(last) });
      pieces.forEach((piece) => {
        if (piece.t === "link") {
          out.push(
            SAFE_HREF.test(piece.href) ? (
              <a key={`${keyBase}-l${key++}`} href={piece.href} target="_blank" rel="noopener noreferrer">
                {piece.label}
              </a>
            ) : (
              <Fragment key={`${keyBase}-l${key++}`}>{piece.label}</Fragment>
            ),
          );
        } else {
          out.push(...emphasize(piece.v, `${keyBase}-t${key++}`));
        }
      });
    });
  return out;
}

export default function Markdown({ text }) {
  const lines = String(text ?? "").replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let paragraph = [];

  const flush = () => {
    if (paragraph.length) {
      blocks.push({ type: "p", text: paragraph.join(" ") });
      paragraph = [];
    }
  };

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const fence = line.match(/^```(\w*)\s*$/);
    if (fence) {
      flush();
      const code = [];
      i++;
      while (i < lines.length && !/^```\s*$/.test(lines[i])) code.push(lines[i++]);
      i++;
      blocks.push({ type: "pre", text: code.join("\n") });
      continue;
    }
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      flush();
      blocks.push({ type: "h", level: Math.min(6, heading[1].length + 3), text: heading[2] });
      i++;
      continue;
    }
    if (/^\s*[-*+]\s+/.test(line)) {
      flush();
      const items = [];
      while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*[-*+]\s+/, ""));
      blocks.push({ type: "ul", items });
      continue;
    }
    if (/^\s*\d+[.)]\s+/.test(line)) {
      flush();
      const items = [];
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*\d+[.)]\s+/, ""));
      blocks.push({ type: "ol", items });
      continue;
    }
    if (/^\s*>\s?/.test(line)) {
      flush();
      const quote = [];
      while (i < lines.length && /^\s*>\s?/.test(lines[i])) quote.push(lines[i++].replace(/^\s*>\s?/, ""));
      blocks.push({ type: "quote", text: quote.join(" ") });
      continue;
    }
    if (!line.trim()) {
      flush();
      i++;
      continue;
    }
    paragraph.push(line.trim());
    i++;
  }
  flush();

  return (
    <div className="md">
      {blocks.map((block, index) => {
        const key = `b${index}`;
        if (block.type === "p") return <p key={key}>{renderInline(block.text, key)}</p>;
        if (block.type === "pre")
          return (
            <pre className="code" key={key}>
              <code>{block.text}</code>
            </pre>
          );
        if (block.type === "h") {
          const Tag = `h${block.level}`;
          return <Tag key={key}>{renderInline(block.text, key)}</Tag>;
        }
        if (block.type === "quote") return <blockquote key={key}>{renderInline(block.text, key)}</blockquote>;
        if (block.type === "ul")
          return (
            <ul key={key}>
              {block.items.map((item, j) => (
                <li key={`${key}-${j}`}>{renderInline(item, `${key}-${j}`)}</li>
              ))}
            </ul>
          );
        return (
          <ol key={key}>
            {block.items.map((item, j) => (
              <li key={`${key}-${j}`}>{renderInline(item, `${key}-${j}`)}</li>
            ))}
          </ol>
        );
      })}
    </div>
  );
}
