matrix9_1 = [
    [
      # One complete block represents all hosters for one meal like e.g. Vorspeise
        [ 1, 4, 7 ], # 1 is hoster for 4 and 7 
        [ 2, 5, 8 ], # 2 is hoster for 5 and 8
        [ 3, 6, 9 ], # 3 is hoster for 6 and 9   
    ],
    # The second block represents the hosters for the next meal like e.g. Hauptspeise
    [
        [ 4, 2, 9 ], # 4 is hoster for 2 and 9
        [ 5, 3, 7 ], # 5 is hoster for 3 and 7   
        [ 6, 1, 8 ], # 6 is hoster for 1 and 8
    ],
    # The third block represents the hosters for the next meal like e.g. Nachspeise
    [
        [7, 2, 6], # 7 is hoster for 2 and 6
        [8, 3, 4], # 8 is hoster for 3 and 4
        [9, 1, 5] # 9 is hoster for 1 and 5
    ]
]
matrix9_2 = [
    [
        [ 1, 4, 5 ],
        [ 2, 6, 8 ],
        [ 3, 7, 9 ],
    ],
    [
        [ 4, 2, 9 ],
        [ 5, 7, 8 ],
        [ 6, 1, 3 ],
    ],
    [
        [ 7, 1, 2 ],
        [ 8, 3, 4 ],
        [ 9, 5, 6 ] 
    ]
]
# matrix9_3 = [
#     [   # Vorspeise hosts: 1, 6, 8
#         [1, 4, 9],    # 1 hosts Hauptspeise (4) and Nachspeise (9)
#         [6, 2, 7],    # 6 hosts Hauptspeise (2) and Nachspeise (7)
#         [8, 3, 5],    # 8 hosts Hauptspeise (3) and Nachspeise (5)
#     ],
#     [   # Hauptspeise hosts: 4, 2, 3
#         [4, 8, 7],    # 4 hosts Vorspeise (8) and Nachspeise (7)
#         [2, 5, 9],    # 2 hosts Nachspeise (5) and Nachspeise (9)
#         [3, 1, 6],    # 3 hosts Vorspeise (1) and Vorspeise (6)
#     ],
#     [   # Nachspeise hosts: 9, 7, 5
#         [9, 3, ],    # 9 hosts Hauptspeise (3) and Vorspeise (6) ---- 9 darf nicht 1,4,5,2,7,5 haben
#         [7, 1, 6],    # 7 hosts Vorspeise (1) and Vorspeise (6) ---- 7 darf nicht 4,8,6,2,9,5,3 haben
#         [5, 4, 6],    # 5 hosts Hauptspeise (4) and Vorspeise (6)
#     ]
# ]
# matrix9_4 = [
#     [   # Vorspeise hosts: 2, 5, 7
#         [2, 6, 9],    # 2 hosts Hauptspeise (6) and Nachspeise (9)
#         [5, 1, 8],    # 5 hosts Hauptspeise (1) and Nachspeise (8)
#         [7, 3, 4],    # 7 hosts Hauptspeise (3) and Nachspeise (4)
#     ],
#     [   # Hauptspeise hosts: 6, 1, 3
#         [6, 2, 7],    # 6 hosts Vorspeise (2) and Nachspeise (7)
#         [1, 5, 9],    # 1 hosts Vorspeise (5) and Nachspeise (9)
#         [3, 4, 8],    # 3 hosts Vorspeise (4) and Nachspeise (8)
#     ],
#     [   # Nachspeise hosts: 9, 8, 4
#         [9, 1, 5],    # 9 hosts Hauptspeise (1) and Vorspeise (5)
#         [8, 3, 2],    # 8 hosts Hauptspeise (3) and Vorspeise (2)
#         [4, 6, 7],    # 4 hosts Hauptspeise (6) and Vorspeise (7)
#     ]
# ]


matrix12_1 = [
    [ 
        [ 1, 5, 9 ], 
        [ 2, 6, 10 ], 
        [ 3, 7, 11 ],
        [ 4, 8, 12 ]
    ], 
    [ 
        [ 5, 10, 11 ],
        [ 6, 9, 12 ],
        [ 7, 1, 4 ],
        [ 8, 2, 3 ]
    ], 
    [ 
        [ 9, 2, 7 ], 
        [ 10, 1, 8 ], 
        [ 11, 4, 6 ],
        [ 12, 3, 5 ]
    ]
]
matrix12_2 = [
    [ 
        [ 1, 5, 9], 
        [ 2, 6, 10 ], 
        [ 3, 7, 11 ],
        [ 4, 8, 12 ]
    ], 
    [ 
        [ 5, 2, 3 ],
        [ 6, 4, 9 ],
        [ 7, 1, 12 ],
        [ 8, 10, 11 ]
    ], 
    [ 
        [ 9, 7, 8 ], 
        [ 10, 3, 1 ], 
        [ 11, 4, 2 ],
        [ 12, 5, 6 ]
    ]	
]
# matrix12_3 = [
#     [   # Vorspeise hosts: 1, 6, 10, 12
#         [1, 8, 3],    # 1 hosts Hauptspeise (8) and Nachspeise (3)
#         [6, 11, 2],   # 6 hosts Hauptspeise (11) and Nachspeise (2)
#         [10, 4, 9],   # 10 hosts Hauptspeise (4) and Nachspeise (9)
#         [12, 7, 5],   # 12 hosts Hauptspeise (7) and Nachspeise (5)
#     ],
#     [   # Hauptspeise hosts: 8, 11, 4, 7
#         [8, 1, 9],    # 8 hosts Vorspeise (1) and Nachspeise (9)
#         [11, 6, 5],   # 11 hosts Vorspeise (6) and Nachspeise (5)
#         [4, 10, 3],   # 4 hosts Vorspeise (10) and Nachspeise (3)
#         [7, 12, 2],   # 7 hosts Vorspeise (12) and Nachspeise (2)
#     ],
#     [   # Nachspeise hosts: 3, 2, 9, 5
#         [3, 1, 4],    # 3 hosts Vorspeise (1) and Hauptspeise (4)
#         [2, 6, 7],    # 2 hosts Vorspeise (6) and Hauptspeise (7)
#         [9, 10, 8],   # 9 hosts Vorspeise (10) and Hauptspeise (8)
#         [5, 12, 11],  # 5 hosts Vorspeise (12) and Hauptspeise (11)
#     ]
# ]

matrix15_1 = [
    [
        [ 1, 5, 9 ],
        [ 2, 6, 10 ],
        [ 3, 7, 11 ],
        [ 4, 14, 12 ],
        [ 13, 8, 15 ]
    ],
    [
        [ 5, 2, 13 ],
        [ 6, 4, 15 ],
        [ 7, 1, 12 ],
        [ 8, 10, 11 ],
        [ 14, 3, 9 ]
    ],
    [
        [ 9, 7, 8 ],
        [ 10, 3, 13 ],
        [ 11, 4, 2 ],
        [ 12, 5, 6 ],
        [ 15, 14, 1 ]
    ]
]
# Matrix 15 is quite computation heavy, so we provide only one template for it.
# matrix15_2 = [
#     [   # Vorspeise hosts: 1, 6, 10, 15, 3
#         [1, 4, 2],    # 1 hosts Hauptspeise (4) and Nachspeise (2)
#         [6, 7, 5],    # 6 hosts Hauptspeise (7) and Nachspeise (5)
#         [10, 8, 9],   # 10 hosts Hauptspeise (8) and Nachspeise (9)
#         [15, 11, 12], # 15 hosts Hauptspeise (11) and Nachspeise (12)
#         [3, 14, 13],  # 3 hosts Hauptspeise (14) and Nachspeise (13)
#     ],
#     [   # Hauptspeise hosts: 4, 7, 8, 11, 14
#         [4, 1, 9],    # 4 hosts Vorspeise (1) and Nachspeise (9)
#         [7, 6, 12],   # 7 hosts Vorspeise (6) and Nachspeise (12)
#         [8, 10, 13],  # 8 hosts Vorspeise (10) and Nachspeise (13)
#         [11, 15, 5],  # 11 hosts Vorspeise (15) and Nachspeise (5)
#         [14, 3, 2],   # 14 hosts Vorspeise (3) and Nachspeise (2)
#     ],
#     [   # Nachspeise hosts: 2, 5, 9, 12, 13
#         [2, 4, 10],   # 2 hosts Hauptspeise (4) and Vorspeise (10)
#         [5, 7, 15],   # 5 hosts Hauptspeise (7) and Vorspeise (15)
#         [9, 8, 1],    # 9 hosts Hauptspeise (8) and Vorspeise (1)
#         [12, 11, 6],  # 12 hosts Hauptspeise (11) and Vorspeise (6)
#         [13, 14, 3],  # 13 hosts Hauptspeise (14) and Vorspeise (3)
#     ]
# ]

matrix4 = [
    [
        [ 1, 3 ], 
        [ 2, 4 ]
    ], 
    [ 
        [ 3, 2 ], 
        [ 4, 1 ]
    ]
]

matrix6 = [
    [ 
        [ 1, 3 ], 
        [ 2, 6 ],
        [ 5, 4 ]
    ], 
    [ 
        [ 3, 2 ], 
        [ 4, 1 ],
        [ 6, 5 ]
    ]
]

matrixes_per_size = {
    9: [matrix9_1, matrix9_2],  # matrix9_3 and matrix9_4 removed - they cause duplicate team crossings
    12: [matrix12_1, matrix12_2],
    15: [matrix15_1],
    4: [matrix4],
    6: [matrix6]
}

def get_matrixes_for_cluster_size(cluster_size: int):
    """
    Returns a matrix for the given cluster size.
    """
    if cluster_size not in matrixes_per_size:
        raise ValueError(f"No matrix defined for cluster size {cluster_size}.")
    
    return matrixes_per_size[cluster_size]