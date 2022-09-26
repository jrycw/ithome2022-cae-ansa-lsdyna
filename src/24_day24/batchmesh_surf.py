import ansa
from ansa import base, batchmesh, constants

from schemas import LSDYNAType

deck = constants.LSDYNA


def main(deck=None):
    deck = deck or constants.LSDYNA

    surface_mpar_str = 'surface.ansa_mpar'
    surface_qual_str = 'surface.ansa_qual'
    cad_file = 'surface.igs'
    r = base.Open(cad_file)

    # topo
    base.Topo(cons='all')

    # geometry fix
    print(f'Running geometry fix...')
    options = ["CRACKS",
               "OVERLAPS",
               "NEEDLE FACES",
               "COLLAPSED CONS",
               "UNCHECKED FACES",
               "UNMESHED MACROS"]
    fix = [1, 1, 1, 1, 1, 1]
    faces = base.CollectEntities(deck, None, 'FACE')
    ret = base.CheckAndFixGeometry(faces, options, fix)
    print(f'Geometry fixed')

    # batch mesh
    print(f'Running batch meshing...')
    scenario1 = batchmesh.GetNewMeshingScenario('scenario1')
    surface_sess = batchmesh.GetNewSession('01_surface')
    surface_mpar = batchmesh.ReadSessionMeshParams(
        surface_sess, surface_mpar_str)
    surface_qual = batchmesh.ReadSessionQualityCriteria(
        surface_sess, surface_qual_str)
    sessions = [surface_sess]
    batchmesh.AddSessionToMeshingScenario(sessions, scenario1)

    surface = base.GetEntity(deck, LSDYNAType.PROPERTY, 1)
    batchmesh.AddPartToSession(surface, surface_sess)
    batchmesh.RunMeshingScenario(scenario1)
    print(f'Batch mesh finished')


if __name__ == '__main__':
    main()
    print('Done!')
