import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Pregunta 4 - Lexer y Parser para la seccion "networks" de docker-compose.yml
 * Implementacion en JAVA. Replica EXACTAMENTE el mismo algoritmo que
 * python/lexer_parser.py y c/lexer_parser.c para que el experimento de
 * carga compare lenguajes, no algoritmos distintos.
 *
 * Se ejecuta sin necesidad de "javac" previo gracias al lanzador de
 * codigo fuente de Java 11+:   java LexerParser.java archivo.yml
 */
public class LexerParser {

    /** Token de linea producido por el LEXER (equivalente a KEY/COLON/DASH/VALUE). */
    static class LineToken {
        int level;
        boolean isList;
        String key;   // puede ser null
        String value; // puede ser null

        LineToken(int level, boolean isList, String key, String value) {
            this.level = level;
            this.isList = isList;
            this.key = key;
            this.value = value;
        }
    }

    /** Nodo generico del arbol: puede representar un mapa o una lista. */
    static class Node {
        LinkedHashMap<String, Object> map;   // si representa un mapa (YAML "objeto")
        List<Object> list;                   // si representa una lista

        static Node asMap() {
            Node n = new Node();
            n.map = new LinkedHashMap<>();
            return n;
        }
    }

    // ------------------------- LEXER -------------------------------------
    static List<LineToken> tokenizeLines(String text) {
        List<LineToken> tokens = new ArrayList<>();
        for (String raw : text.split("\n", -1)) {
            if (raw.trim().isEmpty()) continue;
            int indent = 0;
            while (indent < raw.length() && raw.charAt(indent) == ' ') indent++;
            if (indent % 2 != 0) {
                throw new RuntimeException("Indentacion invalida (no multiplo de 2): " + raw);
            }
            int level = indent / 2;
            String content = raw.substring(indent);
            // quitar espacios finales
            int end = content.length();
            while (end > 0 && Character.isWhitespace(content.charAt(end - 1))) end--;
            content = content.substring(0, end);

            boolean isList = false;
            if (content.startsWith("- ")) {
                isList = true;
                content = content.substring(2);
            } else if (content.equals("-")) {
                isList = true;
                content = "";
            }

            String key = null, value = null;
            int colon = content.indexOf(':');
            if (colon >= 0) {
                key = content.substring(0, colon).trim();
                String v = content.substring(colon + 1).trim();
                value = v.isEmpty() ? null : v;
            } else {
                String v = content.trim();
                value = v.isEmpty() ? null : v;
            }
            tokens.add(new LineToken(level, isList, key, value));
        }
        return tokens;
    }

    // ------------------------- PARSER -------------------------------------
    static class ParserState {
        List<LineToken> toks;
        int i = 0;

        ParserState(List<LineToken> toks) { this.toks = toks; }

        LineToken peek() { return i < toks.size() ? toks.get(i) : null; }
    }

    @SuppressWarnings("unchecked")
    static Object parseBlock(ParserState st, int level) {
        LinkedHashMap<String, Object> node = new LinkedHashMap<>();
        List<Object> listAcc = null;

        while (true) {
            LineToken tok = st.peek();
            if (tok == null || tok.level < level) break;
            if (tok.level > level) throw new RuntimeException("Indentacion inesperada");

            if (tok.isList) {
                if (listAcc == null) listAcc = new ArrayList<>();
                st.i++;
                if (tok.key != null) {
                    LinkedHashMap<String, Object> item = new LinkedHashMap<>();
                    item.put(tok.key, tok.value);
                    Object sub = parseBlock(st, level + 1);
                    if (sub instanceof Map) {
                        item.putAll((Map<String, Object>) sub);
                    }
                    listAcc.add(item);
                } else {
                    listAcc.add(tok.value);
                }
                node.put("__list__", listAcc);
            } else {
                st.i++;
                if (tok.value != null) {
                    node.put(tok.key, tok.value);
                } else {
                    Object child = parseBlock(st, level + 1);
                    node.put(tok.key, child);
                }
            }
        }
        if (listAcc != null && node.size() == 1) {
            return listAcc;
        }
        return node;
    }

    // ------------------------- RESUMEN -------------------------------------
    @SuppressWarnings("unchecked")
    static LinkedHashMap<String, Object> extractNetworksSummary(Object treeObj) {
        Map<String, Object> tree = (Map<String, Object>) treeObj;
        Object networksObj = tree.get("networks");
        List<Map<String, Object>> resumen = new ArrayList<>();

        if (networksObj instanceof Map) {
            Map<String, Object> networks = (Map<String, Object>) networksObj;
            for (Map.Entry<String, Object> e : networks.entrySet()) {
                if (!(e.getValue() instanceof Map)) continue;
                Map<String, Object> props = (Map<String, Object>) e.getValue();
                LinkedHashMap<String, Object> entry = new LinkedHashMap<>();
                entry.put("name", e.getKey());
                entry.put("driver", props.get("driver"));
                entry.put("external", "true".equals(props.get("external")));
                entry.put("attachable", "true".equals(props.get("attachable")));
                List<String> subnets = new ArrayList<>();
                Object ipamObj = props.get("ipam");
                if (ipamObj instanceof Map) {
                    Object configObj = ((Map<String, Object>) ipamObj).get("config");
                    if (configObj instanceof List) {
                        for (Object c : (List<Object>) configObj) {
                            if (c instanceof Map) {
                                Object sn = ((Map<String, Object>) c).get("subnet");
                                if (sn != null) subnets.add(sn.toString());
                            }
                        }
                    }
                }
                entry.put("subnets", subnets);
                resumen.add(entry);
            }
        }
        int nServices = 0;
        Object servicesObj = tree.get("services");
        if (servicesObj instanceof Map) {
            nServices = ((Map<String, Object>) servicesObj).size();
        }
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("n_services", nServices);
        out.put("n_networks", resumen.size());
        out.put("networks", resumen);
        return out;
    }

    static LinkedHashMap<String, Object> parseFile(String path) throws IOException {
        String text = new String(Files.readAllBytes(Paths.get(path)));
        List<LineToken> tokens = tokenizeLines(text);
        ParserState st = new ParserState(tokens);
        Object tree = parseBlock(st, 0);
        return extractNetworksSummary(tree);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.out.println("Uso: java LexerParser.java <archivo docker-compose.yml> [--json]");
            return;
        }
        String path = args[0];
        long t0 = System.nanoTime();
        LinkedHashMap<String, Object> resumen = parseFile(path);
        long t1 = System.nanoTime();

        boolean json = args.length > 1 && args[1].equals("--json");
        if (json) {
            System.out.println(toJson(resumen));
        } else {
            System.out.println("Archivo: " + path);
            System.out.println("  Servicios: " + resumen.get("n_services") + "   Redes: " + resumen.get("n_networks"));
            for (Object net : (List<?>) resumen.get("networks")) {
                System.out.println("   - " + net);
            }
            System.out.printf("Tiempo interno de parseo: %.4f ms%n", (t1 - t0) / 1_000_000.0);
        }
    }

    // Serializador JSON minimo (suficiente para nuestras estructuras Map/List/String/Boolean)
    @SuppressWarnings("unchecked")
    static String toJson(Object o) {
        StringBuilder sb = new StringBuilder();
        writeJson(o, sb);
        return sb.toString();
    }

    @SuppressWarnings("unchecked")
    static void writeJson(Object o, StringBuilder sb) {
        if (o == null) {
            sb.append("null");
        } else if (o instanceof Map) {
            sb.append("{");
            boolean first = true;
            for (Map.Entry<String, Object> e : ((Map<String, Object>) o).entrySet()) {
                if (!first) sb.append(", ");
                first = false;
                sb.append('"').append(e.getKey()).append("\": ");
                writeJson(e.getValue(), sb);
            }
            sb.append("}");
        } else if (o instanceof List) {
            sb.append("[");
            boolean first = true;
            for (Object item : (List<Object>) o) {
                if (!first) sb.append(", ");
                first = false;
                writeJson(item, sb);
            }
            sb.append("]");
        } else if (o instanceof Boolean) {
            sb.append(o.toString());
        } else if (o instanceof Integer || o instanceof Long) {
            sb.append(o.toString());
        } else {
            sb.append('"').append(o.toString().replace("\"", "\\\"")).append('"');
        }
    }
}
