export default function Backlog({ backlog }) {
  return (
    <div className="p-backlog">
      <h3 className="p-backlog-title">Backlog</h3>
      {backlog.length ? (
        <div className="p-suggest-list">
          {backlog.map((b) => (
            <div className="p-suggest" key={`${b.source}-${b.id}`}>
              <div className="p-suggest-title-sm">{b.title}</div>
              <div className="p-suggest-why">{b.meta}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-backlog-clear">Nothing waiting — your backlog is clear.</div>
      )}
    </div>
  );
}