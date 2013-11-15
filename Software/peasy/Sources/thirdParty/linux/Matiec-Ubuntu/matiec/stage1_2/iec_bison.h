/* A Bison parser, made by GNU Bison 2.5.  */

/* Bison interface for Yacc-like parsers in C
   
      Copyright (C) 1984, 1989-1990, 2000-2011 Free Software Foundation, Inc.
   
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.
   
   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* "%code requires" blocks.  */

/* Line 2068 of yacc.c  */
#line 255 "iec_bison.yy"

/* define a new data type to store the locations, so we can also store
 * the filename in which the token is expressed.
 */
/* NOTE: since this code will be placed in the iec_bison.h header file,
 * as well as the iec.cc file that also includes the iec_bison.h header file,
 * declaring the typedef struct yyltype__local here would result in a 
 * compilation error when compiling iec.cc, as this struct would be
 * declared twice.
 * We therefore use the #if !defined YYLTYPE ...
 * to make sure only the first declaration is parsed by the C++ compiler.
 */
#if ! defined YYLTYPE && ! defined YYLTYPE_IS_DECLARED
typedef struct YYLTYPE {
    int         first_line;
    int         first_column;
    const char *first_file;
    long int    first_order;
    int         last_line;
    int         last_column;
    const char *last_file;
    long int    last_order;
} YYLTYPE;
#define YYLTYPE_IS_DECLARED 1
#define YYLTYPE_IS_TRIVIAL 1
#endif




/* Line 2068 of yacc.c  */
#line 69 "iec_bison.h"

/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     END_OF_INPUT = 0,
     BOGUS_TOKEN_ID = 258,
     prev_declared_variable_name_token = 259,
     prev_declared_direct_variable_token = 260,
     prev_declared_fb_name_token = 261,
     prev_declared_simple_type_name_token = 262,
     prev_declared_subrange_type_name_token = 263,
     prev_declared_enumerated_type_name_token = 264,
     prev_declared_array_type_name_token = 265,
     prev_declared_structure_type_name_token = 266,
     prev_declared_string_type_name_token = 267,
     prev_declared_derived_function_name_token = 268,
     prev_declared_derived_function_block_name_token = 269,
     prev_declared_program_type_name_token = 270,
     disable_code_generation_pragma_token = 271,
     enable_code_generation_pragma_token = 272,
     pragma_token = 273,
     EN = 274,
     ENO = 275,
     identifier_token = 276,
     integer_token = 277,
     binary_integer_token = 278,
     octal_integer_token = 279,
     hex_integer_token = 280,
     real_token = 281,
     safeboolean_true_literal_token = 282,
     safeboolean_false_literal_token = 283,
     boolean_true_literal_token = 284,
     boolean_false_literal_token = 285,
     FALSE = 286,
     TRUE = 287,
     single_byte_character_string_token = 288,
     double_byte_character_string_token = 289,
     fixed_point_token = 290,
     fixed_point_d_token = 291,
     integer_d_token = 292,
     fixed_point_h_token = 293,
     integer_h_token = 294,
     fixed_point_m_token = 295,
     integer_m_token = 296,
     fixed_point_s_token = 297,
     integer_s_token = 298,
     fixed_point_ms_token = 299,
     integer_ms_token = 300,
     end_interval_token = 301,
     erroneous_interval_token = 302,
     T_SHARP = 303,
     D_SHARP = 304,
     BYTE = 305,
     WORD = 306,
     DWORD = 307,
     LWORD = 308,
     LREAL = 309,
     REAL = 310,
     SINT = 311,
     INT = 312,
     DINT = 313,
     LINT = 314,
     USINT = 315,
     UINT = 316,
     UDINT = 317,
     ULINT = 318,
     WSTRING = 319,
     STRING = 320,
     BOOL = 321,
     TIME = 322,
     DATE = 323,
     DATE_AND_TIME = 324,
     DT = 325,
     TIME_OF_DAY = 326,
     TOD = 327,
     SAFEBYTE = 328,
     SAFEWORD = 329,
     SAFEDWORD = 330,
     SAFELWORD = 331,
     SAFELREAL = 332,
     SAFEREAL = 333,
     SAFESINT = 334,
     SAFEINT = 335,
     SAFEDINT = 336,
     SAFELINT = 337,
     SAFEUSINT = 338,
     SAFEUINT = 339,
     SAFEUDINT = 340,
     SAFEULINT = 341,
     SAFEWSTRING = 342,
     SAFESTRING = 343,
     SAFEBOOL = 344,
     SAFETIME = 345,
     SAFEDATE = 346,
     SAFEDATE_AND_TIME = 347,
     SAFEDT = 348,
     SAFETIME_OF_DAY = 349,
     SAFETOD = 350,
     ANY = 351,
     ANY_DERIVED = 352,
     ANY_ELEMENTARY = 353,
     ANY_MAGNITUDE = 354,
     ANY_NUM = 355,
     ANY_REAL = 356,
     ANY_INT = 357,
     ANY_BIT = 358,
     ANY_STRING = 359,
     ANY_DATE = 360,
     ASSIGN = 361,
     DOTDOT = 362,
     TYPE = 363,
     END_TYPE = 364,
     ARRAY = 365,
     OF = 366,
     STRUCT = 367,
     END_STRUCT = 368,
     direct_variable_token = 369,
     incompl_location_token = 370,
     VAR_INPUT = 371,
     VAR_OUTPUT = 372,
     VAR_IN_OUT = 373,
     VAR_EXTERNAL = 374,
     VAR_GLOBAL = 375,
     END_VAR = 376,
     RETAIN = 377,
     NON_RETAIN = 378,
     R_EDGE = 379,
     F_EDGE = 380,
     AT = 381,
     standard_function_name_token = 382,
     FUNCTION = 383,
     END_FUNCTION = 384,
     CONSTANT = 385,
     standard_function_block_name_token = 386,
     FUNCTION_BLOCK = 387,
     END_FUNCTION_BLOCK = 388,
     VAR_TEMP = 389,
     VAR = 390,
     PROGRAM = 391,
     END_PROGRAM = 392,
     ACTION = 393,
     END_ACTION = 394,
     TRANSITION = 395,
     END_TRANSITION = 396,
     FROM = 397,
     TO = 398,
     PRIORITY = 399,
     INITIAL_STEP = 400,
     STEP = 401,
     END_STEP = 402,
     L = 403,
     D = 404,
     SD = 405,
     DS = 406,
     SL = 407,
     N = 408,
     P = 409,
     P0 = 410,
     P1 = 411,
     prev_declared_global_var_name_token = 412,
     prev_declared_program_name_token = 413,
     prev_declared_resource_name_token = 414,
     prev_declared_configuration_name_token = 415,
     CONFIGURATION = 416,
     END_CONFIGURATION = 417,
     TASK = 418,
     RESOURCE = 419,
     ON = 420,
     END_RESOURCE = 421,
     VAR_CONFIG = 422,
     VAR_ACCESS = 423,
     WITH = 424,
     SINGLE = 425,
     INTERVAL = 426,
     READ_WRITE = 427,
     READ_ONLY = 428,
     EOL = 429,
     sendto_identifier_token = 430,
     LD = 431,
     LDN = 432,
     ST = 433,
     STN = 434,
     NOT = 435,
     S = 436,
     R = 437,
     S1 = 438,
     R1 = 439,
     CLK = 440,
     CU = 441,
     CD = 442,
     PV = 443,
     IN = 444,
     PT = 445,
     AND = 446,
     AND2 = 447,
     OR = 448,
     XOR = 449,
     ANDN = 450,
     ANDN2 = 451,
     ORN = 452,
     XORN = 453,
     ADD = 454,
     SUB = 455,
     MUL = 456,
     DIV = 457,
     MOD = 458,
     GT = 459,
     GE = 460,
     EQ = 461,
     LT = 462,
     LE = 463,
     NE = 464,
     CAL = 465,
     CALC = 466,
     CALCN = 467,
     RET = 468,
     RETC = 469,
     RETCN = 470,
     JMP = 471,
     JMPC = 472,
     JMPCN = 473,
     SENDTO = 474,
     OPER_NE = 475,
     OPER_GE = 476,
     OPER_LE = 477,
     OPER_EXP = 478,
     RETURN = 479,
     IF = 480,
     THEN = 481,
     ELSIF = 482,
     ELSE = 483,
     END_IF = 484,
     CASE = 485,
     END_CASE = 486,
     FOR = 487,
     BY = 488,
     DO = 489,
     END_FOR = 490,
     WHILE = 491,
     END_WHILE = 492,
     REPEAT = 493,
     UNTIL = 494,
     END_REPEAT = 495,
     EXIT = 496
   };
#endif
/* Tokens.  */
#define END_OF_INPUT 0
#define BOGUS_TOKEN_ID 258
#define prev_declared_variable_name_token 259
#define prev_declared_direct_variable_token 260
#define prev_declared_fb_name_token 261
#define prev_declared_simple_type_name_token 262
#define prev_declared_subrange_type_name_token 263
#define prev_declared_enumerated_type_name_token 264
#define prev_declared_array_type_name_token 265
#define prev_declared_structure_type_name_token 266
#define prev_declared_string_type_name_token 267
#define prev_declared_derived_function_name_token 268
#define prev_declared_derived_function_block_name_token 269
#define prev_declared_program_type_name_token 270
#define disable_code_generation_pragma_token 271
#define enable_code_generation_pragma_token 272
#define pragma_token 273
#define EN 274
#define ENO 275
#define identifier_token 276
#define integer_token 277
#define binary_integer_token 278
#define octal_integer_token 279
#define hex_integer_token 280
#define real_token 281
#define safeboolean_true_literal_token 282
#define safeboolean_false_literal_token 283
#define boolean_true_literal_token 284
#define boolean_false_literal_token 285
#define FALSE 286
#define TRUE 287
#define single_byte_character_string_token 288
#define double_byte_character_string_token 289
#define fixed_point_token 290
#define fixed_point_d_token 291
#define integer_d_token 292
#define fixed_point_h_token 293
#define integer_h_token 294
#define fixed_point_m_token 295
#define integer_m_token 296
#define fixed_point_s_token 297
#define integer_s_token 298
#define fixed_point_ms_token 299
#define integer_ms_token 300
#define end_interval_token 301
#define erroneous_interval_token 302
#define T_SHARP 303
#define D_SHARP 304
#define BYTE 305
#define WORD 306
#define DWORD 307
#define LWORD 308
#define LREAL 309
#define REAL 310
#define SINT 311
#define INT 312
#define DINT 313
#define LINT 314
#define USINT 315
#define UINT 316
#define UDINT 317
#define ULINT 318
#define WSTRING 319
#define STRING 320
#define BOOL 321
#define TIME 322
#define DATE 323
#define DATE_AND_TIME 324
#define DT 325
#define TIME_OF_DAY 326
#define TOD 327
#define SAFEBYTE 328
#define SAFEWORD 329
#define SAFEDWORD 330
#define SAFELWORD 331
#define SAFELREAL 332
#define SAFEREAL 333
#define SAFESINT 334
#define SAFEINT 335
#define SAFEDINT 336
#define SAFELINT 337
#define SAFEUSINT 338
#define SAFEUINT 339
#define SAFEUDINT 340
#define SAFEULINT 341
#define SAFEWSTRING 342
#define SAFESTRING 343
#define SAFEBOOL 344
#define SAFETIME 345
#define SAFEDATE 346
#define SAFEDATE_AND_TIME 347
#define SAFEDT 348
#define SAFETIME_OF_DAY 349
#define SAFETOD 350
#define ANY 351
#define ANY_DERIVED 352
#define ANY_ELEMENTARY 353
#define ANY_MAGNITUDE 354
#define ANY_NUM 355
#define ANY_REAL 356
#define ANY_INT 357
#define ANY_BIT 358
#define ANY_STRING 359
#define ANY_DATE 360
#define ASSIGN 361
#define DOTDOT 362
#define TYPE 363
#define END_TYPE 364
#define ARRAY 365
#define OF 366
#define STRUCT 367
#define END_STRUCT 368
#define direct_variable_token 369
#define incompl_location_token 370
#define VAR_INPUT 371
#define VAR_OUTPUT 372
#define VAR_IN_OUT 373
#define VAR_EXTERNAL 374
#define VAR_GLOBAL 375
#define END_VAR 376
#define RETAIN 377
#define NON_RETAIN 378
#define R_EDGE 379
#define F_EDGE 380
#define AT 381
#define standard_function_name_token 382
#define FUNCTION 383
#define END_FUNCTION 384
#define CONSTANT 385
#define standard_function_block_name_token 386
#define FUNCTION_BLOCK 387
#define END_FUNCTION_BLOCK 388
#define VAR_TEMP 389
#define VAR 390
#define PROGRAM 391
#define END_PROGRAM 392
#define ACTION 393
#define END_ACTION 394
#define TRANSITION 395
#define END_TRANSITION 396
#define FROM 397
#define TO 398
#define PRIORITY 399
#define INITIAL_STEP 400
#define STEP 401
#define END_STEP 402
#define L 403
#define D 404
#define SD 405
#define DS 406
#define SL 407
#define N 408
#define P 409
#define P0 410
#define P1 411
#define prev_declared_global_var_name_token 412
#define prev_declared_program_name_token 413
#define prev_declared_resource_name_token 414
#define prev_declared_configuration_name_token 415
#define CONFIGURATION 416
#define END_CONFIGURATION 417
#define TASK 418
#define RESOURCE 419
#define ON 420
#define END_RESOURCE 421
#define VAR_CONFIG 422
#define VAR_ACCESS 423
#define WITH 424
#define SINGLE 425
#define INTERVAL 426
#define READ_WRITE 427
#define READ_ONLY 428
#define EOL 429
#define sendto_identifier_token 430
#define LD 431
#define LDN 432
#define ST 433
#define STN 434
#define NOT 435
#define S 436
#define R 437
#define S1 438
#define R1 439
#define CLK 440
#define CU 441
#define CD 442
#define PV 443
#define IN 444
#define PT 445
#define AND 446
#define AND2 447
#define OR 448
#define XOR 449
#define ANDN 450
#define ANDN2 451
#define ORN 452
#define XORN 453
#define ADD 454
#define SUB 455
#define MUL 456
#define DIV 457
#define MOD 458
#define GT 459
#define GE 460
#define EQ 461
#define LT 462
#define LE 463
#define NE 464
#define CAL 465
#define CALC 466
#define CALCN 467
#define RET 468
#define RETC 469
#define RETCN 470
#define JMP 471
#define JMPC 472
#define JMPCN 473
#define SENDTO 474
#define OPER_NE 475
#define OPER_GE 476
#define OPER_LE 477
#define OPER_EXP 478
#define RETURN 479
#define IF 480
#define THEN 481
#define ELSIF 482
#define ELSE 483
#define END_IF 484
#define CASE 485
#define END_CASE 486
#define FOR 487
#define BY 488
#define DO 489
#define END_FOR 490
#define WHILE 491
#define END_WHILE 492
#define REPEAT 493
#define UNTIL 494
#define END_REPEAT 495
#define EXIT 496




#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef union YYSTYPE
{

/* Line 2068 of yacc.c  */
#line 286 "iec_bison.yy"

    symbol_c 	*leaf;
    list_c	*list;
    char 	*ID;	/* token value */



/* Line 2068 of yacc.c  */
#line 578 "iec_bison.h"
} YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
#endif

extern YYSTYPE yylval;

#if ! defined YYLTYPE && ! defined YYLTYPE_IS_DECLARED
typedef struct YYLTYPE
{
  int first_line;
  int first_column;
  int last_line;
  int last_column;
} YYLTYPE;
# define yyltype YYLTYPE /* obsolescent; will be withdrawn */
# define YYLTYPE_IS_DECLARED 1
# define YYLTYPE_IS_TRIVIAL 1
#endif

extern YYLTYPE yylloc;

