struct FPNodeList;
struct FPNode;
struct FPHeader;
struct FPTree;
struct FPSearchState;
struct FPSearchStack;

typedef struct FPNode {
  unsigned int             _item_index;
  unsigned int                _support;
  struct FPNode*               _parent;
  struct FPHeader*             _header;
  struct FPNodeList*         _children;
  struct FPNode**    _children_by_item;
} fp_node_t;

typedef struct FPNodeList {
  unsigned int           _size;
  unsigned int    _actual_size;
  struct FPNode**        _list;
} fp_node_list_t;

typedef struct FPHeader {
  unsigned int       _item_index;
  unsigned int          _support;
  struct FPNodeList*      _nodes;
} fp_header_t;

typedef struct FPSearchState {
  unsigned int          _projected_item_index;
  unsigned int*              _removes_to_undo;
  unsigned int*           _items_with_removes;
  struct FPSearchState*                 _next;
} fp_search_state_t;

typedef struct FPSearchStack {
  unsigned int _size;
  struct FPSearchState* _top;
} fp_search_stack_t;

typedef struct FPSolution {
  unsigned int*      _solution;
  struct FPSolution*     _next;
  struct FPSolution*     _prev;
} fp_solution_t;

fp_node_list_t* init_fp_node_list();
fp_node_t* get_fp_node(fp_node_list_t* list, unsigned int index);
void add_fp_node_to_list(fp_node_list_t* list, fp_node_t* item);
void remove_fp_node_from_list(fp_node_list_t* list, unsigned int fp_node_index);
void undo_fp_node_remove(fp_node_list_t* list);
void free_fp_node_list(fp_node_list_t* list);

fp_node_t* init_fp_node(unsigned int item_index, fp_node_t* parent, fp_header_t* header);
void add_child_node(fp_node_t* parent_node, unsigned int child_item_index, fp_header_t* child_header);
void remove_child_fp_node(fp_node_t* parent_node, fp_node_t* child_node);
void print_fp_node(fp_node_t* node);

void fp_search_state_push(fp_search_stack* stack, unsigned int item_to_project);
void fp_search_state_free(fp_search_state* state);
fp_search_state* fp_search_state_pop(fp_search_stack* stack);

void add_fp_solution(unsigned int* frequent_pattern);
