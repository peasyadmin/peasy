/*
 *  matiec - a compiler for the programming languages defined in IEC 61131-3
 *
 *  Copyright (C) 2003-2011  Mario de Sousa (msousa@fe.up.pt)
 *  Copyright (C) 2007-2011  Laurent Bessard and Edouard Tisserant
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *
 * This code is made available on the understanding that it will not be
 * used in safety-critical situations without a full and competent review.
 */

/*
 * An IEC 61131-3 compiler.
 *
 * Based on the
 * FINAL DRAFT - IEC 61131-3, 2nd Ed. (2001-12-10)
 *
 */

/* Determine the data type of a variable.
 * The variable may be a simple variable, a function block instance, a
 * struture element within a data structured type (a struct or a fb), or
 * an array element.
 * A mixture of array element of a structure element of a structure element
 * of a .... is also suported!
 *
 *  example:
 *    window.points[1].coordinate.x
 *    window.points[1].colour
 *    etc... ARE ALLOWED!
 *
 * This class must be passed the scope within which the
 * variable was declared, and the variable name...
 *
 *
 *
 *
 *
 * This class has several members, depending on the exact data the caller
 * is looking for...
 *
 *    - item i: we can get either the name of the data type(A),
 *              or it's declaration (B)
 *             (notice however that some variables belong to a data type that does
 *              not have a name, only a declaration as in
 *              VAR a: ARRAY [1..3] of INT; END_VAR
 *             )
 *    - item ii: we can get either the direct data type (1), 
 *               or the base type (2)
 * 
 *   By direct type, I mean the data type of the variable. By base type, I 
 * mean the data type on which the direct type is based on. For example, in 
 * a subrange on INT, the direct type is the subrange itself, while the 
 * base type is INT.
 * e.g.
 *   This means that if we find that the variable is of type MY_INT,
 *   which was previously declared to be
 *   TYPE MY_INT: INT := 9;
 *   option (1) will return MY_INT
 *   option (2) will return INT
 * 
 *
 * Member functions:
 * ================
 *   get_basetype_decl()  ---> returns 2B 
 *   get_type_id()        ---> returns 1A
 * 
 *   Since we haven't yet needed them, we don't yet implement
 *   get_basetype_id()    ----> would return 2A
 *   get_type_decl()      ----> would return 1B
 */ 


/*
 * TODO: this code has a memory leak...
 *       We call 'new' in several locations, but bever get to 'delete' the object instances...
 */
#include "absyntax_utils.hh"


search_varfb_instance_type_c::search_varfb_instance_type_c(symbol_c *search_scope): search_var_instance_decl(search_scope) {
  this->decompose_var_instance_name = NULL;
  this->current_structelement_name = NULL;
  this->current_typeid = NULL;
  this->current_basetypeid = NULL;
}

symbol_c *search_varfb_instance_type_c::get_type_decl(symbol_c *variable_name) {
  this->current_structelement_name = NULL;
  this->current_typeid = NULL;
  this->current_basetypeid = NULL;
  this->decompose_var_instance_name = new decompose_var_instance_name_c(variable_name);
  if (NULL == decompose_var_instance_name) ERROR;

  /* find the part of the variable name that will appear in the
   * variable declaration, for e.g., in window.point.x, this would be
   * window!
   */
  symbol_c *var_name_part = decompose_var_instance_name->next_part();
  if (NULL == var_name_part) ERROR;

  /* Now we try to find the variable instance declaration, to determine its type... */
  symbol_c *var_decl = search_var_instance_decl.get_decl(var_name_part);
  if (NULL == var_decl) ERROR;

  /* if it is a struct or function block, we must search the type
   * of the struct or function block member.
   * This is done by this class visiting the var_decl.
   * This class, while visiting, will recursively call
   * decompose_var_instance_name->get_next() when and if required...
   */
  symbol_c *res = (symbol_c *)var_decl->accept(*this);
  /* NOTE: A Null result is not really an internal compiler error, but rather an error in 
   * the IEC 61131-3 source code being compiled. This means we cannot just abort the compiler with ERROR.
   * //   if (NULL == res) ERROR;
   */
  if (NULL == res) return NULL;

  /* make sure that we have decomposed all structure elements of the variable name */
  symbol_c *var_name = decompose_var_instance_name->next_part();
  /* NOTE: A non-NULL result is not really an internal compiler error, but rather an error in 
   * the IEC 61131-3 source code being compiled. 
   *  (for example, 'int_var.struct_elem' in the source code, when 'int_var' is a simple integer,
   *   and not a structure, will result in this result being non-NULL!)
   * This means we cannot just abort the compiler with ERROR.
   * //   if (NULL != var_name) ERROR;
   */
  if (NULL != var_name) return NULL;

  return res;
}


symbol_c *search_varfb_instance_type_c::get_basetype_decl(symbol_c *variable_name) {
  symbol_c *res = get_type_decl(variable_name);
  if (NULL == res) return NULL;
  return (symbol_c *)base_type(res);
}  


unsigned int search_varfb_instance_type_c::get_vartype(symbol_c *variable_name) {
  this->current_structelement_name = NULL;
  this->current_typeid = NULL;
  this->current_basetypeid = NULL;
  this->is_complex = false;
  this->decompose_var_instance_name = new decompose_var_instance_name_c(variable_name);
  if (NULL == decompose_var_instance_name) ERROR;

  /* find the part of the variable name that will appear in the
   * variable declaration, for e.g., in window.point.x, this would be
   * window!
   */
  symbol_c *var_name_part = decompose_var_instance_name->next_part();
  if (NULL == var_name_part) ERROR;

  /* Now we try to find the variable instance declaration, to determine its type... */
  symbol_c *var_decl = search_var_instance_decl.get_decl(var_name_part);
  if (NULL == var_decl) {
    /* variable instance declaration not found! */
    return 0;
  }

  /* if it is a struct or function block, we must search the type
   * of the struct or function block member.
   * This is done by this class visiting the var_decl.
   * This class, while visiting, will recursively call
   * decompose_var_instance_name->get_next() when and if required...
   */
  var_decl->accept(*this);
  unsigned int res = search_var_instance_decl.get_vartype();
  
  /* make sure that we have decomposed all structure elements of the variable name */
  symbol_c *var_name = decompose_var_instance_name->next_part();
  if (NULL != var_name) ERROR;

  return res;
}

symbol_c *search_varfb_instance_type_c::get_type_id(symbol_c *variable_name) {
  this->current_typeid = NULL;
  symbol_c *vartype = this->get_type_decl(variable_name);
  if (this->current_typeid != NULL)
    return this->current_typeid;
  else
    return vartype;
}

bool search_varfb_instance_type_c::type_is_complex(void) {
  return this->is_complex;
}

/* a helper function... */
void *search_varfb_instance_type_c::visit_list(list_c *list)	{
  if (NULL == current_structelement_name) ERROR;

  for(int i = 0; i < list->n; i++) {
    void *res = list->elements[i]->accept(*this);
    if (res != NULL)
      return res;
  }
  /* not found! */
  return NULL;
}

/* a helper function... */
void *search_varfb_instance_type_c::base_type(symbol_c *symbol)	{
    search_base_type_c search_base_type;
    return symbol->accept(search_base_type);
}

/* We override the base class' visitor to identifier_c.
 * This is so because the base class does not consider a function block
 * to be a type, unlike this class that allows a variable instance
 * of a function block type...
 */
void *search_varfb_instance_type_c::visit(identifier_c *type_name) {
  /* we only store the new type id if none had been found yet.
   * Since we will recursively carry on looking at the base type 
   * to determine the base type declaration and id, we must only set this variable
   * the first time.
   * e.g. TYPE myint1_t : int    := 1;
   *           myint2_t : int1_t := 2;
   *           myint3_t : int2_t := 3;
   *      END_TYPE;
   *      VAR
   *          myint1 : myint1_t;
   *          myint2 : myint2_t;
   *          myint3 : myint3_t;
   *      END_VAR
   *        
   *     If we ask for typeid of     myint3, it must return myint3_t
   *     If we ask for basetypeid of myint3, it must return int
   *
   *     When determining the data type of myint3, we will recursively go all the way
   *     down to int, but we must still only store myint3_t as the base type id.
   */
  if (NULL == this->current_typeid)
    this->current_typeid = type_name;
  this->current_basetypeid = type_name;

  /* look up the type declaration... */
  symbol_c *fb_decl = function_block_type_symtable.find_value(type_name);
  if (fb_decl != function_block_type_symtable.end_value())
    /* Type declaration found!! */
    return fb_decl->accept(*this);

  /* No. It is not a function block, so we let
   * the base class take care of it...
   */
  return search_base_type_c::visit(type_name);
}

/********************************/
/* B 1.3.3 - Derived data types */
/********************************/

/*  identifier ':' array_spec_init */
void *search_varfb_instance_type_c::visit(array_type_declaration_c *symbol) {
  return symbol->array_spec_init->accept(*this);
}
    
/* array_specification [ASSIGN array_initialization] */
/* array_initialization may be NULL ! */
void *search_varfb_instance_type_c::visit(array_spec_init_c *symbol) {
  return symbol->array_specification->accept(*this);
}

/* ARRAY '[' array_subrange_list ']' OF non_generic_type_name */
void *search_varfb_instance_type_c::visit(array_specification_c *symbol) {
  this->is_complex = true;
  this->current_typeid = symbol;
  return symbol->non_generic_type_name->accept(*this);
}

/*  structure_type_name ':' structure_specification */
/* NOTE: this is only used inside a TYPE ... END_TYPE declaration. 
 * It is never used directly when declaring a new variable! 
 */
void *search_varfb_instance_type_c::visit(structure_type_declaration_c *symbol) {
  this->is_complex = true;

  if (NULL == current_structelement_name) ERROR;
  return symbol->structure_specification->accept(*this);
  /* NOTE: structure_specification will point to either a
   *       initialized_structure_c
   *       OR A
   *       structure_element_declaration_list_c
   */
}

/* structure_type_name ASSIGN structure_initialization */
/* structure_initialization may be NULL ! */
// SYM_REF2(initialized_structure_c, structure_type_name, structure_initialization)
/* NOTE: only the initialized structure is ever used when declaring a new variable instance */
void *search_varfb_instance_type_c::visit(initialized_structure_c *symbol)	{
  this->is_complex = true;
  if (NULL != current_structelement_name) ERROR;
  
  /* make sure that we have decomposed all structure elements of the variable name */
  symbol_c *var_name = decompose_var_instance_name->next_part();
  if (NULL == var_name) {
    /* this is it... !
     * No need to look any further...
     * Note also that, unlike for the struct types, a function block may
     * not be defined based on another (i.e. no inheritance is allowed),
     * so this function block is already the most base type.
     * We simply return it.
     */
    return (void *)symbol;
  }

  /* reset current_type_id because of new structure element part */
  this->current_typeid = NULL;

  /* look for the var_name in the structure declaration */
  current_structelement_name = var_name;

  /* recursively find out the data type of current_structelement_name... */
  return symbol->structure_type_name->accept(*this);
}

/* helper symbol for structure_declaration */
/* structure_declaration:  STRUCT structure_element_declaration_list END_STRUCT */
/* structure_element_declaration_list structure_element_declaration ';' */
void *search_varfb_instance_type_c::visit(structure_element_declaration_list_c *symbol)	{
  if (NULL == current_structelement_name) ERROR;
  /* now search the structure declaration */
  return visit_list(symbol);
}

/*  structure_element_name ':' spec_init */
void *search_varfb_instance_type_c::visit(structure_element_declaration_c *symbol) {
  if (NULL == current_structelement_name) ERROR;

  if (compare_identifiers(symbol->structure_element_name, current_structelement_name) == 0) {
    current_structelement_name = NULL;
    /* found the type of the element we were looking for! */
    return symbol->spec_init->accept(*this);
  }  

  /* Did not find the type of the element we were looking for! */
  /* Will keep looking... */
  return NULL;
}

/* helper symbol for structure_initialization */
/* structure_initialization: '(' structure_element_initialization_list ')' */
/* structure_element_initialization_list ',' structure_element_initialization */
void *search_varfb_instance_type_c::visit(structure_element_initialization_list_c *symbol) {ERROR; return NULL;} /* should never get called... */
/*  structure_element_name ASSIGN value */
void *search_varfb_instance_type_c::visit(structure_element_initialization_c *symbol) {ERROR; return NULL;} /* should never get called... */



/**************************************/
/* B.1.5 - Program organization units */
/**************************************/
/*****************************/
/* B 1.5.2 - Function Blocks */
/*****************************/
/*  FUNCTION_BLOCK derived_function_block_name io_OR_other_var_declarations function_block_body END_FUNCTION_BLOCK */
// SYM_REF4(function_block_declaration_c, fblock_name, var_declarations, fblock_body, unused)
void *search_varfb_instance_type_c::visit(function_block_declaration_c *symbol) {
  /* make sure that we have decomposed all structure elements of the variable name */
  symbol_c *var_name = decompose_var_instance_name->next_part();
  if (NULL == var_name) {
    /* this is it... !
     * No need to look any further...
     * Note also that, unlike for the struct types, a function block may
     * not be defined based on another (i.e. no inheritance is allowed),
     * so this function block is already the most base type.
     * We simply return it.
     */
    return (void *)symbol;
   }

   /* reset current_type_id because of new structure element part */
   this->current_typeid = NULL;

   /* now search the function block declaration for the variable... */
   search_var_instance_decl_c search_decl(symbol);
   symbol_c *var_decl = search_decl.get_decl(var_name);
   if (NULL == var_decl) {
     /* variable instance declaration not found! */
     return NULL;
   }
#if 0
   /* We have found the declaration.
    * Should we look any further?
    */
   var_name = decompose_var_instance_name->next_part();
   if (NULL == var_name) {
     /* this is it... ! */
     return base_type(var_decl);
   }

  current_structelement_name = var_name;
  /* recursively find out the data type of var_name... */
  return symbol->var_declarations->accept(*this);
#endif
  /* carry on recursively, in case the variable has more elements to be decomposed... */
  return var_decl->accept(*this);
}
