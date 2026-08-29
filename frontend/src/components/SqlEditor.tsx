import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorView } from '@codemirror/view';

interface SqlEditorProps {
  value: string;
  onChange?: (val: string) => void;
  readOnly?: boolean;
  placeholder?: string;
  minHeight?: string;
  height?: string;
}

const baseTheme = EditorView.theme({
  '&': {
    fontSize: '0.875rem',
  },
  '.cm-content': {
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', ui-monospace, monospace",
    padding: '12px 0',
  },
  '.cm-gutters': {
    backgroundColor: 'rgb(17 24 39)',
    borderRight: '1px solid rgb(31 41 55)',
    color: 'rgb(75 85 99)',
  },
  '.cm-activeLineGutter': {
    backgroundColor: 'rgb(31 41 55)',
  },
  '.cm-activeLine': {
    backgroundColor: 'rgba(255,255,255,0.03)',
  },
  '.cm-placeholder': {
    color: 'rgb(75 85 99)',
    fontStyle: 'italic',
  },
});

export default function SqlEditor({
  value,
  onChange,
  readOnly = false,
  placeholder = 'Enter your SQL query here…',
  minHeight = '200px',
}: SqlEditorProps) {
  return (
    <div
      className="rounded-lg border border-gray-700 overflow-hidden"
      style={{ minHeight }}
    >
      <CodeMirror
        value={value}
        onChange={onChange}
        extensions={[sql(), baseTheme]}
        theme={oneDark}
        readOnly={readOnly}
        placeholder={placeholder}
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          highlightActiveLineGutter: true,
          highlightActiveLine: true,
          autocompletion: !readOnly,
          closeBrackets: !readOnly,
          indentOnInput: !readOnly,
        }}
        style={{ minHeight }}
      />
    </div>
  );
}
