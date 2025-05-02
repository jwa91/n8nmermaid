scripts/analyze_n8n_workflow_examples.py:25:16: UP038 Use `X | Y` in `isinstance` call instead of `(X, Y)`
   |
23 |         for k, v in params.items():
24 |             new_key = f"{parent_key}{sep}{k}" if parent_key else k
25 |             if isinstance(v, (dict, list)):
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^ UP038
26 |                 items.extend(flatten_parameters(v, new_key, sep=sep))
27 |             else:
   |
   = help: Convert to `X | Y`

scripts/analyze_n8n_workflow_examples.py:32:16: UP038 Use `X | Y` in `isinstance` call instead of `(X, Y)`
   |
30 |         for i, v in enumerate(params):
31 |             new_key = f"{parent_key}{sep}[{i}]" if parent_key else f"[{i}]"
32 |             if isinstance(v, (dict, list)):
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^ UP038
33 |                 items.extend(flatten_parameters(v, new_key, sep=sep))
34 |             else:
   |
   = help: Convert to `X | Y`

scripts/analyze_n8n_workflow_examples.py:38:20: UP038 Use `X | Y` in `isinstance` call instead of `(X, Y)`
   |
36 |                 # Usually, we care more about dicts inside lists
37 |                 # Might adjust this if lists of primitives are important
38 |                 if isinstance(v, (dict, list)):
   |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^ UP038
39 |                     items.append((new_key, v))
40 |                 # If we want to capture primitive values directly in lists:
   |
   = help: Convert to `X | Y`

scripts/analyze_n8n_workflow_examples.py:67:23: C414 Unnecessary `list()` call within `sorted()`
   |
65 |     markdown.append("\nThis section lists all unique parameter keys found across all node types, after flattening nested structures.\n…
66 |     if all_unique_keys:
67 |         sorted_keys = sorted(list(all_unique_keys))
   |                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ C414
68 |         for key in sorted_keys:
69 |             markdown.append(f"- `{key}`")
   |
   = help: Remove the inner `list()` call

scripts/analyze_n8n_workflow_examples.py:82:20: C414 Unnecessary `list()` call within `sorted()`
   |
80 |         for node_type in sorted_node_types:
81 |             markdown.append(f"\n### Node Type: `{node_type}`")
82 |             keys = sorted(list(keys_by_node_type[node_type]))
   |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ C414
83 |             if keys:
84 |                 for key in keys:
   |
   = help: Remove the inner `list()` call

src/n8nmermaid/api/helpers.py:33:89: E501 Line too long (95 > 88)
   |
31 |     Args:
32 |         request_body: The parsed request body (ApiMermaidRequest or ApiReportRequest).
33 |         command: The specific command being executed ('generate_mermaid' or 'generate_report').
   |                                                                                         ^^^^^^^ E501
34 |
35 |     Returns:
   |

src/n8nmermaid/api/helpers.py:51:89: E501 Line too long (103 > 88)
   |
49 |         report_params = request_body.params
50 |     else:
51 |         logger.error("Invalid request body type passed to API helper: %s", type(request_body).__name__)
   |                                                                                         ^^^^^^^^^^^^^^^ E501
52 |         raise HTTPException(
53 |             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
   |

src/n8nmermaid/api/helpers.py:61:89: E501 Line too long (105 > 88)
   |
59 |             workflow_data=request_body.workflow_data,
60 |             command=command,
61 |             mermaid_params=mermaid_params if mermaid_params is not None else MermaidGenerationParamsV2(),
   |                                                                                         ^^^^^^^^^^^^^^^^^ E501
62 |             report_params=report_params,
63 |         )
   |

src/n8nmermaid/api/helpers.py:77:89: E501 Line too long (92 > 88)
   |
75 |         ) from e
76 |     except ValueError as e:
77 |         logger.error("Validation error during API request processing: %s", e, exc_info=True)
   |                                                                                         ^^^^ E501
78 |         raise HTTPException(
79 |             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
   |

src/n8nmermaid/api/main.py:33:89: E501 Line too long (93 > 88)
   |
31 |     logger.error("OrchestratorError caught: %s", exc, exc_info=False)
32 |     return JSONResponse(
33 |         status_code=status.HTTP_400_BAD_REQUEST, content={"detail": f"Analysis Error: {exc}"}
   |                                                                                         ^^^^^ E501
34 |     )
   |

src/n8nmermaid/api/main.py:62:89: E501 Line too long (98 > 88)
   |
60 |     app = FastAPI(
61 |         title="n8n-mermaid API",
62 |         description="API for analyzing n8n workflows and generating Mermaid diagrams or reports.",
   |                                                                                         ^^^^^^^^^^ E501
63 |         version="2.0.0",
64 |         lifespan=lifespan
   |

src/n8nmermaid/api/routers/mermaid.py:31:89: E501 Line too long (102 > 88)
   |
29 |     - `subgraph_direction`: Layout direction inside subgraphs. Default: BT.
30 |     - `show_credentials`: If true, display credential names on nodes. Default: false.
31 |     - `show_key_parameters`: If true, display key parameters (like AI model) on nodes. Default: false.
   |                                                                                         ^^^^^^^^^^^^^^ E501
32 |     - `subgraph_display_mode`: How to handle clusters ('subgraph', 'simple_node', 'separate_clusters'). Default: 'subgraph'.
   |

src/n8nmermaid/api/routers/mermaid.py:32:89: E501 Line too long (124 > 88)
   |
30 |     - `show_credentials`: If true, display credential names on nodes. Default: false.
31 |     - `show_key_parameters`: If true, display key parameters (like AI model) on nodes. Default: false.
32 |     - `subgraph_display_mode`: How to handle clusters ('subgraph', 'simple_node', 'separate_clusters'). Default: 'subgraph'.
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ E501
33 |
34 | Returns a dictionary where the key `main` holds the primary diagram. If `subgraph_display_mode` is 'separate_clusters', additional key…
   |

src/n8nmermaid/api/routers/mermaid.py:34:89: E501 Line too long (180 > 88)
   |
32 | …mple_node', 'separate_clusters'). Default: 'subgraph'.
33 | …
34 | …f `subgraph_display_mode` is 'separate_clusters', additional keys will contain diagrams for each cluster root.
   |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ E501
35 | …
36 | …
   |

src/n8nmermaid/api/routers/mermaid.py:37:89: E501 Line too long (113 > 88)
   |
35 | """,
36 |     responses={
37 |         status.HTTP_400_BAD_REQUEST: {"model": ApiErrorDetail, "description": "Analysis or Orchestration Error"},
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^^^^^ E501
38 |         status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ApiErrorDetail, "description": "Invalid Input Data"},
39 |         status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApiErrorDetail, "description": "Internal Server Error"},
   |

src/n8nmermaid/api/routers/mermaid.py:38:89: E501 Line too long (109 > 88)
   |
36 |     responses={
37 |         status.HTTP_400_BAD_REQUEST: {"model": ApiErrorDetail, "description": "Analysis or Orchestration Error"},
38 |         status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ApiErrorDetail, "description": "Invalid Input Data"},
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^ E501
39 |         status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApiErrorDetail, "description": "Internal Server Error"},
40 |     },
   |

src/n8nmermaid/api/routers/mermaid.py:39:89: E501 Line too long (113 > 88)
   |
37 |         status.HTTP_400_BAD_REQUEST: {"model": ApiErrorDetail, "description": "Analysis or Orchestration Error"},
38 |         status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ApiErrorDetail, "description": "Invalid Input Data"},
39 |         status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApiErrorDetail, "description": "Internal Server Error"},
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^^^^^ E501
40 |     },
41 | )
   |

src/n8nmermaid/api/routers/mermaid.py:42:89: E501 Line too long (91 > 88)
   |
40 |     },
41 | )
42 | async def generate_mermaid_endpoint(request_body: ApiMermaidRequest) -> ApiMermaidResponse:
   |                                                                                         ^^^ E501
43 |     """
44 |     Handles requests to generate Mermaid diagrams.
   |

src/n8nmermaid/api/routers/mermaid.py:62:89: E501 Line too long (98 > 88)
   |
61 |         if not isinstance(result, dict):
62 |             logger.error("Mermaid generation returned unexpected type: %s", type(result).__name__)
   |                                                                                         ^^^^^^^^^^ E501
63 |             raise HTTPException(
64 |                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
   |

src/n8nmermaid/api/routers/report.py:28:89: E501 Line too long (240 > 88)
   |
26 | …
27 | …
28 | …ntials"]`). Available types: `stats`, `credentials`, `agents`, `node_parameters`, `analysis_json`. Note: `analysis_json` cannot be combined with other types.
   |       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ E501
29 | …'text'. Note: Currently only 'text' is fully supported for combined reports, 'analysis_json' always returns JSON.
   |

src/n8nmermaid/api/routers/report.py:29:89: E501 Line too long (196 > 88)
   |
27 | …
28 | …credentials"]`). Available types: `stats`, `credentials`, `agents`, `node_parameters`, `analysis_json`. Note: `analysis_json` cannot …
29 | …ult: 'text'. Note: Currently only 'text' is fully supported for combined reports, 'analysis_json' always returns JSON.
   |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ E501
30 | …
31 | …alysis_json` is requested).
   |

src/n8nmermaid/api/routers/report.py:31:89: E501 Line too long (105 > 88)
   |
29 |     - `output_format`: Format of the report ('text', 'markdown', 'json'). Default: 'text'. Note: Currently only 'text' is fully suppor…
30 |
31 | Returns the generated report content as a single string (or JSON string if `analysis_json` is requested).
   |                                                                                         ^^^^^^^^^^^^^^^^^ E501
32 | """,
33 |     responses={
   |

src/n8nmermaid/api/routers/report.py:34:89: E501 Line too long (113 > 88)
   |
32 | """,
33 |     responses={
34 |         status.HTTP_400_BAD_REQUEST: {"model": ApiErrorDetail, "description": "Analysis or Orchestration Error"},
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^^^^^ E501
35 |         status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ApiErrorDetail, "description": "Invalid Input Data"},
36 |         status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApiErrorDetail, "description": "Internal Server Error"},
   |

src/n8nmermaid/api/routers/report.py:35:89: E501 Line too long (109 > 88)
   |
33 |     responses={
34 |         status.HTTP_400_BAD_REQUEST: {"model": ApiErrorDetail, "description": "Analysis or Orchestration Error"},
35 |         status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ApiErrorDetail, "description": "Invalid Input Data"},
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^ E501
36 |         status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApiErrorDetail, "description": "Internal Server Error"},
37 |     },
   |

src/n8nmermaid/api/routers/report.py:36:89: E501 Line too long (113 > 88)
   |
34 |         status.HTTP_400_BAD_REQUEST: {"model": ApiErrorDetail, "description": "Analysis or Orchestration Error"},
35 |         status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ApiErrorDetail, "description": "Invalid Input Data"},
36 |         status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApiErrorDetail, "description": "Internal Server Error"},
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^^^^^ E501
37 |     },
38 | )
   |

src/n8nmermaid/api/routers/report.py:59:89: E501 Line too long (97 > 88)
   |
58 |         if not isinstance(result, str):
59 |             logger.error("Report generation returned unexpected type: %s", type(result).__name__)
   |                                                                                         ^^^^^^^^^ E501
60 |             raise HTTPException(
61 |                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
   |

src/n8nmermaid/api/routers/report.py:62:89: E501 Line too long (93 > 88)
   |
60 |             raise HTTPException(
61 |                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
62 |                 detail="Internal server error: Report generator returned unexpected format.",
   |                                                                                         ^^^^^ E501
63 |             )
   |

src/n8nmermaid/api/schemas.py:13:89: E501 Line too long (95 > 88)
   |
11 | class ApiMermaidRequest(BaseModel):
12 |     """Request body schema for the /mermaid endpoint."""
13 |     workflow_data: dict[str, Any] = Field(..., description="The raw n8n workflow JSON object.")
   |                                                                                         ^^^^^^^ E501
14 |     params: MermaidGenerationParamsV2 = Field(default_factory=MermaidGenerationParamsV2, description="Mermaid generation parameters.")
   |

src/n8nmermaid/api/schemas.py:14:89: E501 Line too long (134 > 88)
   |
12 |     """Request body schema for the /mermaid endpoint."""
13 |     workflow_data: dict[str, Any] = Field(..., description="The raw n8n workflow JSON object.")
14 |     params: MermaidGenerationParamsV2 = Field(default_factory=MermaidGenerationParamsV2, description="Mermaid generation parameters.")
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ E501
15 |
16 | class ApiReportRequest(BaseModel):
   |

src/n8nmermaid/api/schemas.py:18:89: E501 Line too long (95 > 88)
   |
16 | class ApiReportRequest(BaseModel):
17 |     """Request body schema for the /report endpoint."""
18 |     workflow_data: dict[str, Any] = Field(..., description="The raw n8n workflow JSON object.")
   |                                                                                         ^^^^^^^ E501
19 |     params: ReportGenerationParamsV2 = Field(..., description="Report generation parameters.")
   |

src/n8nmermaid/api/schemas.py:19:89: E501 Line too long (94 > 88)
   |
17 |     """Request body schema for the /report endpoint."""
18 |     workflow_data: dict[str, Any] = Field(..., description="The raw n8n workflow JSON object.")
19 |     params: ReportGenerationParamsV2 = Field(..., description="Report generation parameters.")
   |                                                                                         ^^^^^^ E501
20 |
21 | class ApiMermaidResponse(BaseModel):
   |

src/n8nmermaid/api/schemas.py:23:89: E501 Line too long (131 > 88)
   |
21 | class ApiMermaidResponse(BaseModel):
22 |     """Response schema for the /mermaid endpoint."""
23 |     diagrams: dict[str, str] = Field(description="Dictionary of generated Mermaid diagrams. Key 'main' holds the primary diagram.")
   |                                                                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ E501
24 |
25 | class ApiReportResponse(BaseModel):
   |

src/n8nmermaid/core/orchestrator_v2.py:26:7: N818 Exception name `OrchestratorErrorV2` should be named with an Error suffix
   |
26 | class OrchestratorErrorV2(Exception):
   |       ^^^^^^^^^^^^^^^^^^^ N818
27 |     """Custom exception for failures within the V2 orchestration process."""
   |

Found 33 errors.
No fixes available (5 hidden fixes can be enabled with the `--unsafe-fixes` option).
