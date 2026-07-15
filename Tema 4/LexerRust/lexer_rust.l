%{
#include <stdio.h>

int linea = 1;
%}

%%

"let"           { printf("[LINEA %d] TOKEN: KW_LET        | Lexema: %s\n", linea, yytext); }
"mut"           { printf("[LINEA %d] TOKEN: KW_MUT        | Lexema: %s\n", linea, yytext); }
"fn"            { printf("[LINEA %d] TOKEN: KW_FN         | Lexema: %s\n", linea, yytext); }
"if"            { printf("[LINEA %d] TOKEN: KW_IF         | Lexema: %s\n", linea, yytext); }
"else"          { printf("[LINEA %d] TOKEN: KW_ELSE       | Lexema: %s\n", linea, yytext); }
"while"         { printf("[LINEA %d] TOKEN: KW_WHILE      | Lexema: %s\n", linea, yytext); }
"for"           { printf("[LINEA %d] TOKEN: KW_FOR        | Lexema: %s\n", linea, yytext); }
"return"        { printf("[LINEA %d] TOKEN: KW_RETURN     | Lexema: %s\n", linea, yytext); }
"true"          { printf("[LINEA %d] TOKEN: KW_TRUE       | Lexema: %s\n", linea, yytext); }
"false"         { printf("[LINEA %d] TOKEN: KW_FALSE      | Lexema: %s\n", linea, yytext); }
"i32"           { printf("[LINEA %d] TOKEN: TIPO_I32      | Lexema: %s\n", linea, yytext); }
"f64"           { printf("[LINEA %d] TOKEN: TIPO_F64      | Lexema: %s\n", linea, yytext); }
"bool"          { printf("[LINEA %d] TOKEN: TIPO_BOOL     | Lexema: %s\n", linea, yytext); }
"String"        { printf("[LINEA %d] TOKEN: TIPO_STRING   | Lexema: %s\n", linea, yytext); }
"println!"      { printf("[LINEA %d] TOKEN: MACRO_PRINTLN | Lexema: %s\n", linea, yytext); }

[0-9]+\.[0-9]+  { printf("[LINEA %d] TOKEN: LIT_FLOTANTE  | Lexema: %s\n", linea, yytext); }
[0-9]+          { printf("[LINEA %d] TOKEN: LIT_ENTERO    | Lexema: %s\n", linea, yytext); }
\"[^\"]*\"      { printf("[LINEA %d] TOKEN: LIT_CADENA    | Lexema: %s\n", linea, yytext); }

"+"             { printf("[LINEA %d] TOKEN: OP_SUMA       | Lexema: %s\n", linea, yytext); }
"-"             { printf("[LINEA %d] TOKEN: OP_RESTA      | Lexema: %s\n", linea, yytext); }
"*"             { printf("[LINEA %d] TOKEN: OP_MULT       | Lexema: %s\n", linea, yytext); }
"/"             { printf("[LINEA %d] TOKEN: OP_DIV        | Lexema: %s\n", linea, yytext); }
"=="            { printf("[LINEA %d] TOKEN: OP_IGUAL      | Lexema: %s\n", linea, yytext); }
"!="            { printf("[LINEA %d] TOKEN: OP_DISTINTO   | Lexema: %s\n", linea, yytext); }
">="            { printf("[LINEA %d] TOKEN: OP_MAYOR_IGU  | Lexema: %s\n", linea, yytext); }
"<="            { printf("[LINEA %d] TOKEN: OP_MENOR_IGU  | Lexema: %s\n", linea, yytext); }
">"             { printf("[LINEA %d] TOKEN: OP_MAYOR      | Lexema: %s\n", linea, yytext); }
"<"             { printf("[LINEA %d] TOKEN: OP_MENOR      | Lexema: %s\n", linea, yytext); }
"="             { printf("[LINEA %d] TOKEN: OP_ASIGNACION | Lexema: %s\n", linea, yytext); }

"{"             { printf("[LINEA %d] TOKEN: LLAVE_ABR     | Lexema: %s\n", linea, yytext); }
"}"             { printf("[LINEA %d] TOKEN: LLAVE_CIE     | Lexema: %s\n", linea, yytext); }
"("             { printf("[LINEA %d] TOKEN: PAREN_ABR     | Lexema: %s\n", linea, yytext); }
")"             { printf("[LINEA %d] TOKEN: PAREN_CIE     | Lexema: %s\n", linea, yytext); }
";"             { printf("[LINEA %d] TOKEN: PUNTO_COMA    | Lexema: %s\n", linea, yytext); }
":"             { printf("[LINEA %d] TOKEN: DOS_PUNTOS    | Lexema: %s\n", linea, yytext); }
","             { printf("[LINEA %d] TOKEN: COMA          | Lexema: %s\n", linea, yytext); }

[a-zA-Z_][a-zA-Z0-9_]*  { printf("[LINEA %d] TOKEN: IDENTIFICADOR | Lexema: %s\n", linea, yytext); }

\/\/[^\n]*      { /* ignorar comentarios de linea */ }
\n              { linea++; }
[ \t]+          { /* ignorar espacios */ }
.               { printf("[LINEA %d] ERROR LEXICO: caracter no reconocido '%s'\n", linea, yytext); }

%%

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *f = fopen(argv[1], "r");
        if (!f) {
            printf("Error: no se pudo abrir el archivo %s\n", argv[1]);
            return 1;
        }
        yyin = f;
    }
    yylex();
    return 0;
}

int yywrap() {
    return 1;
}