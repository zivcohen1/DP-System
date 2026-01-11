grammar DPDSL;

/* ===== PARSER RULES ===== */

query
    : select_clause from_clause where_clause? group_by_clause? limit_clause? EOF
    ;

select_clause
    : SELECT select_item (',' select_item)*
    ;

select_item
    : expression (AS? alias=identifier)?
    ;

expression
    : function_name '(' '*' ')'                               # CountStar
    | function_name '(' expression (OF '[' budget ']')? ')'   # Aggregation
    | label? column_ref                                       # ColumnReference
    | expression operator expression                          # BinaryOp
    | '(' expression ')'                                      # Parens
    | INT                                                     # Literal
    | FLOAT                                                   # FloatLiteral
    | STRING                                                  # StringLiteral
    ;

column_ref
    : identifier ('.' identifier)?
    ;

from_clause
    : FROM table_source (',' table_source)*
    ;

table_source
    : identifier (AS? alias=identifier)?                                              # SimpleTable
    | identifier (AS? alias1=identifier)? join_type? JOIN identifier (AS? alias2=identifier)? ON expression  # JoinTable
    ;

join_type
    : INNER | LEFT | RIGHT | FULL
    ;

where_clause
    : WHERE expression
    ;

group_by_clause
    : GROUP BY group_item (',' group_item)*
    ;

group_item
    : label? column_ref
    ;

limit_clause
    : LIMIT INT
    ;

/* ===== LEXER RULES ===== */

// Operators (before keywords to avoid conflicts)
operator: '+' | '-' | '*' | '/' | '>' | '<' | '=' | '>=' | '<=' | '!=' | AND | OR | LIKE ;

// Budget (epsilon value)
budget: FLOAT | INT ;

// Keywords (must come before identifier to have precedence) - case insensitive
SELECT: [Ss][Ee][Ll][Ee][Cc][Tt] ;
FROM: [Ff][Rr][Oo][Mm] ;
WHERE: [Ww][Hh][Ee][Rr][Ee] ;
GROUP: [Gg][Rr][Oo][Uu][Pp] ;
BY: [Bb][Yy] ;
LIMIT: [Ll][Ii][Mm][Ii][Tt] ;
AS: [Aa][Ss] ;
OF: [Oo][Ff] ;
JOIN: [Jj][Oo][Ii][Nn] ;
ON: [Oo][Nn] ;
INNER: [Ii][Nn][Nn][Ee][Rr] ;
LEFT: [Ll][Ee][Ff][Tt] ;
RIGHT: [Rr][Ii][Gg][Hh][Tt] ;
FULL: [Ff][Uu][Ll][Ll] ;
AND: [Aa][Nn][Dd] ;
OR: [Oo][Rr] ;
LIKE: [Ll][Ii][Kk][Ee] ;

// Labels - case insensitive
label: PRIVATE | PUBLIC ;
PRIVATE: [Pp][Rr][Ii][Vv][Aa][Tt][Ee] ;
PUBLIC: [Pp][Uu][Bb][Ll][Ii][Cc] ;

// Functions - case insensitive
function_name: SUM | COUNT | MAX | AVG | MIN ;
SUM: [Ss][Uu][Mm] ;
COUNT: [Cc][Oo][Uu][Nn][Tt] ;
MAX: [Mm][Aa][Xx] ;
AVG: [Aa][Vv][Gg] ;
MIN: [Mm][Ii][Nn] ;

// Identifiers and Literals
identifier: ID ;
ID: [a-zA-Z_][a-zA-Z0-9_]* ;

INT: [0-9]+ ;
FLOAT: '-'? [0-9]+ '.' [0-9]+ ;
STRING: '\'' (~['\r\n])* '\'' ;

// Whitespace
WS: [ \t\r\n]+ -> skip ;

// Comments (optional but helpful)
LINE_COMMENT: '--' ~[\r\n]* -> skip ;
BLOCK_COMMENT: '/*' .*? '*/' -> skip ;
