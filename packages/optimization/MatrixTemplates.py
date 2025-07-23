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


matrixes_per_size = {
    9: [matrix9_1, matrix9_2],
    12: [ matrix12_1, matrix12_2 ]
}

def get_matrixes_for_cluster_size(cluster_size: int):
    """
    Returns a matrix for the given cluster size.
    """
    if cluster_size not in matrixes_per_size:
        raise ValueError(f"No matrix defined for cluster size {cluster_size}.")
    
    return matrixes_per_size[cluster_size]